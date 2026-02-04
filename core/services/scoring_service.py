"""
评分业务服务类
"""
from typing import Dict, List, Optional
from decimal import Decimal
import logging

from core.repositories.scoring_repository import ScoringRepository
from core.repositories.project_repository import ProjectRepository
from app.utils.scoring import ScoringCalculator
from config.scoring_rules import SCORING_DIMENSIONS

logger = logging.getLogger(__name__)


class ScoringService:
    """评分业务服务类"""

    def __init__(self):
        self.scoring_repo = ScoringRepository()
        self.project_repo = ProjectRepository()
        self.calculator = ScoringCalculator()

    def get_scoring_structure(self) -> Dict:
        """获取评分结构（维度和指标）"""
        try:
            dimensions = self.scoring_repo.get_all_dimensions()

            structure = {}
            for dimension in dimensions:
                indicators = self.scoring_repo.get_indicators_by_dimension(dimension['id'])
                structure[dimension['dimension_code']] = {
                    'id': dimension['id'],
                    'name': dimension['dimension_name'],
                    'weight': float(dimension['weight']),
                    'max_score': float(dimension['max_score']),
                    'indicators': [
                        {
                            'id': ind['id'],
                            'code': ind['indicator_code'],
                            'name': ind['indicator_name'],
                            'weight': float(ind['weight']),
                            'max_score': float(ind['max_score']),
                            'scoring_criteria': ind['scoring_criteria']
                        }
                        for ind in indicators
                    ]
                }

            return structure
        except Exception as e:
            logger.error(f"Error getting scoring structure: {str(e)}")
            raise

    def submit_indicator_score(
        self,
        project_id: int,
        dimension_id: int,
        indicator_id: int,
        raw_score: Decimal,
        scorer_id: int,
        scorer_comment: Optional[str] = None
    ) -> Dict:
        """
        提交单个指标评分

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # 获取指标信息
            from app.utils.database import get_db_connection
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT weight, max_score FROM scoring_indicators WHERE id = %s"
                    cursor.execute(sql, (indicator_id,))
                    indicator = cursor.fetchone()

            if not indicator:
                return {'success': False, 'message': '指标不存在'}

            # 计算加权得分
            score, weighted_score = self.calculator.calculate_indicator_score(
                Decimal(str(raw_score)),
                Decimal(str(indicator['max_score'])),
                Decimal(str(indicator['weight']))
            )

            # 保存评分
            score_id = self.scoring_repo.save_score(
                project_id, dimension_id, indicator_id,
                score, weighted_score, scorer_id, scorer_comment
            )

            logger.info(f"Saved score: project={project_id}, indicator={indicator_id}, score={score}")

            return {
                'success': True,
                'message': '评分保存成功',
                'data': {
                    'score_id': score_id,
                    'score': float(score),
                    'weighted_score': float(weighted_score)
                }
            }
        except Exception as e:
            logger.error(f"Error submitting score: {str(e)}")
            return {'success': False, 'message': f'保存失败: {str(e)}'}

    def calculate_and_save_dimension_score(
        self,
        project_id: int,
        dimension_id: int
    ) -> Dict:
        """
        计算并保存维度汇总得分

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # 获取该维度的权重
            from app.utils.database import get_db_connection
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT weight FROM scoring_dimensions WHERE id = %s", (dimension_id,))
                    dim_result = cursor.fetchone()
                    if not dim_result:
                        return {'success': False, 'message': '维度不存在'}
                    dimension_weight = Decimal(str(dim_result['weight']))

            # 获取该维度下的所有评分
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT score, weighted_score
                        FROM project_scores
                        WHERE project_id = %s AND dimension_id = %s
                    """
                    cursor.execute(sql, (project_id, dimension_id))
                    scores = cursor.fetchall()

            if not scores:
                return {'success': False, 'message': '该维度下暂无评分数据'}

            # 计算维度汇总（传入维度权重）
            total_score, weighted_total = self.calculator.calculate_dimension_score(
                scores,
                dimension_weight=dimension_weight
            )

            # 保存汇总
            summary_id = self.scoring_repo.save_dimension_summary(
                project_id, dimension_id, total_score, weighted_total
            )

            return {
                'success': True,
                'message': '维度汇总计算完成',
                'data': {
                    'summary_id': summary_id,
                    'total_score': float(total_score),
                    'weighted_total': float(weighted_total)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating dimension score: {str(e)}")
            return {'success': False, 'message': f'计算失败: {str(e)}'}

    def calculate_project_total_score(self, project_id: int) -> Dict:
        """
        计算项目总分并评级

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # 获取各维度汇总
            summaries = self.scoring_repo.get_dimension_summaries(project_id)

            if len(summaries) < 3:
                # 检查是否所有13个指标都有评分
                from app.utils.database import get_db_connection
                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT COUNT(DISTINCT indicator_id) as scored_count FROM project_scores WHERE project_id = %s",
                            (project_id,)
                        )
                        result = cursor.fetchone()
                        scored_count = result['scored_count'] if result else 0

                # 总共13个指标，如果全部评分完成，计算总分
                if scored_count >= 13:
                    # 重新计算所有维度的汇总（确保数据同步）
                    for dim_code in ['POLICY', 'LAYOUT', 'EXECUTION']:
                        from app.utils.database import get_db_connection
                        with get_db_connection() as conn:
                            with conn.cursor() as cursor:
                                cursor.execute(
                                    "SELECT id FROM scoring_dimensions WHERE dimension_code = %s",
                                    (dim_code,)
                                )
                                dim_result = cursor.fetchone()
                                if dim_result:
                                    self.calculate_and_save_dimension_score(project_id, dim_result['id'])

                    # 重新获取维度汇总
                    summaries = self.scoring_repo.get_dimension_summaries(project_id)

                if len(summaries) < 3:
                    return {'success': False, 'message': f'评分不完整，已完成 {len(summaries)}/3 个维度，共 {scored_count}/13 个指标'}

            # 构建维度得分字典（使用未加权的维度总分）
            # 维度的权重体现在其满分上（60、30、10分），不需要再次加权
            dimension_scores = {
                item['dimension_code']: Decimal(str(item['total_score']))
                for item in summaries
            }

            # 计算总分和等级
            total_score, grade = self.calculator.calculate_total_score(dimension_scores)

            # 保存总分（使用未加权的维度得分）
            total_id = self.scoring_repo.save_project_total(
                project_id,
                total_score,
                dimension_scores.get('POLICY', Decimal('0')),
                dimension_scores.get('LAYOUT', Decimal('0')),
                dimension_scores.get('EXECUTION', Decimal('0')),
                grade
            )

            # 更新排名
            self._update_project_rankings()

            # 更新项目状态
            self.project_repo.update_status(project_id, 'completed')

            logger.info(f"Calculated total score for project {project_id}: {total_score} ({grade})")

            return {
                'success': True,
                'message': '总分计算完成',
                'data': {
                    'total_id': total_id,
                    'total_score': float(total_score),
                    'grade': grade,
                    'grade_name': self.calculator.get_grade_name(grade)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating total score: {str(e)}")
            return {'success': False, 'message': f'计算失败: {str(e)}'}

    def _update_project_rankings(self):
        """更新所有项目排名"""
        try:
            # 获取所有已完成的项目总分
            all_totals = self.scoring_repo.get_all_project_totals()

            # 计算排名
            ranked = self.calculator.calculate_project_ranking(all_totals)

            # 更新数据库
            self.scoring_repo.update_project_rankings(ranked)

            logger.info("Updated project rankings")
        except Exception as e:
            logger.error(f"Error updating rankings: {str(e)}")

    def get_project_scoring_detail(self, project_id: int) -> Dict:
        """获取项目评分详情"""
        try:
            # 获取项目基本信息
            project = self.project_repo.get_by_id(project_id)
            if not project:
                return {'success': False, 'message': '项目不存在'}

            # 获取所有评分记录
            scores = self.scoring_repo.get_project_scores(project_id)

            # 获取总分
            total = self.scoring_repo.get_project_total_score(project_id)

            # 按维度组织评分数据
            dimension_details = {}
            for score in scores:
                dim_code = score['dimension_code']
                if dim_code not in dimension_details:
                    dimension_details[dim_code] = {
                        'name': score['dimension_name'],
                        'indicators': []
                    }
                dimension_details[dim_code]['indicators'].append({
                    'code': score['indicator_code'],
                    'name': score['indicator_name'],
                    'score': float(score['score']),
                    'weighted_score': float(score['weighted_score']),
                    'scorer': score['scorer_name'],
                    'comment': score['scorer_comment'],
                    'scored_at': score['scored_at'].isoformat() if score['scored_at'] else None
                })

            return {
                'success': True,
                'data': {
                    'project': {
                        'id': project['id'],
                        'code': project['project_code'],
                        'name': project['project_name'],
                        'status': project['status']
                    },
                    'dimensions': dimension_details,
                    'total_score': float(total['total_score']) if total else None,
                    'grade': total['grade'] if total else None,
                    'grade_name': self.calculator.get_grade_name(total['grade']) if total and total['grade'] else None,
                    'rank': total['rank_in_period'] if total else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting scoring detail: {str(e)}")
            return {'success': False, 'message': f'获取失败: {str(e)}'}

    def get_grade_distribution(self) -> Dict[str, int]:
        """获取等级分布统计"""
        try:
            from app.utils.database import get_db_connection
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT grade, COUNT(*) as count
                        FROM project_total_scores
                        GROUP BY grade
                    """
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    return {r['grade']: r['count'] for r in results}
        except Exception as e:
            logger.error(f"Error getting grade distribution: {str(e)}")
            return {}

    def get_dimension_averages(self) -> Dict[str, float]:
        """获取各维度平均分"""
        try:
            from app.utils.database import get_db_connection
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT sd.dimension_code, AVG(ss.weighted_total) as avg_score
                        FROM scoring_summaries ss
                        JOIN scoring_dimensions sd ON ss.dimension_id = sd.id
                        GROUP BY sd.dimension_code
                    """
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    return {r['dimension_code']: float(r['avg_score']) for r in results}
        except Exception as e:
            logger.error(f"Error getting dimension averages: {str(e)}")
            return {}
