"""
评分计算逻辑模块
"""
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
import logging

from config.scoring_rules import SCORING_DIMENSIONS, GRADING_STANDARDS

logger = logging.getLogger(__name__)


class ScoringCalculator:
    """评分计算器"""

    @staticmethod
    def calculate_indicator_score(
        raw_score: Decimal,
        max_score: Decimal,
        weight: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        计算单个指标的加权得分

        Args:
            raw_score: 原始评分
            max_score: 该指标最高分
            weight: 权重百分比

        Returns:
            (原始评分, 加权得分)
        """
        # 验证分数不超过最高分
        if raw_score > max_score:
            raw_score = max_score
        if raw_score < 0:
            raw_score = Decimal('0')

        # 计算加权得分：原始分数 * (权重 / 100)
        weighted_score = (raw_score * weight) / Decimal('100')

        # 保留2位小数
        raw_score = raw_score.quantize(Decimal('0.01'))
        weighted_score = weighted_score.quantize(Decimal('0.01'))

        return raw_score, weighted_score

    @staticmethod
    def calculate_dimension_score(
        indicator_scores: List[Dict]
    ) -> Tuple[Decimal, Decimal]:
        """
        计算维度的总分和加权总分

        Args:
            indicator_scores: 该维度下所有指标的评分列表
                [{'score': Decimal, 'weighted_score': Decimal}, ...]

        Returns:
            (维度总分, 维度加权总分)
        """
        if not indicator_scores:
            return Decimal('0'), Decimal('0')

        total_score = sum(item['score'] for item in indicator_scores)
        weighted_total = sum(item['weighted_score'] for item in indicator_scores)

        total_score = total_score.quantize(Decimal('0.01'))
        weighted_total = weighted_total.quantize(Decimal('0.01'))

        return total_score, weighted_total

    @staticmethod
    def calculate_total_score(
        dimension_weighted_scores: Dict[str, Decimal]
    ) -> Tuple[Decimal, str]:
        """
        计算项目总分并评定等级

        Args:
            dimension_weighted_scores: 各维度加权分数
                {'POLICY': Decimal('45.5'), 'LAYOUT': Decimal('22.8'), ...}

        Returns:
            (总分, 等级代码)
        """
        total_score = sum(dimension_weighted_scores.values())
        total_score = total_score.quantize(Decimal('0.01'))

        # 评定等级
        grade = ScoringCalculator._determine_grade(total_score)

        return total_score, grade

    @staticmethod
    def _determine_grade(total_score: Decimal) -> str:
        """根据总分确定等级"""
        score = float(total_score)

        if score >= GRADING_STANDARDS['excellent']['min']:
            return 'excellent'
        elif score >= GRADING_STANDARDS['good']['min']:
            return 'good'
        elif score >= GRADING_STANDARDS['qualified']['min']:
            return 'qualified'
        else:
            return 'unqualified'

    @staticmethod
    def get_grade_name(grade_code: str) -> str:
        """获取等级名称"""
        return GRADING_STANDARDS.get(grade_code, {}).get('name', '未知')

    @staticmethod
    def get_grade_color(grade_code: str) -> str:
        """获取等级颜色"""
        return GRADING_STANDARDS.get(grade_code, {}).get('color', '#999')

    @staticmethod
    def validate_score_completeness(
        dimension_scores: Dict[str, List[Dict]]
    ) -> Tuple[bool, List[str]]:
        """
        验证评分完整性

        Args:
            dimension_scores: 各维度评分数据

        Returns:
            (是否完整, 缺失的指标列表)
        """
        missing_indicators = []

        for dim_code, dimension in SCORING_DIMENSIONS.items():
            for indicator in dimension['indicators']:
                # 检查该指标是否有评分
                indicator_found = False
                for score_record in dimension_scores.get(dim_code, []):
                    if score_record.get('indicator_code') == indicator['code']:
                        indicator_found = True
                        if score_record.get('score') is None:
                            missing_indicators.append(f"{dimension['name']}-{indicator['name']}")
                        break

                if not indicator_found:
                    missing_indicators.append(f"{dimension['name']}-{indicator['name']}")

        is_complete = len(missing_indicators) == 0
        return is_complete, missing_indicators

    @staticmethod
    def calculate_project_ranking(
        project_scores: List[Dict]
    ) -> List[Dict]:
        """
        计算项目排名

        Args:
            project_scores: 项目总分列表
                [{'project_id': 1, 'total_score': 85.5, ...}, ...]

        Returns:
            添加了rank字段的项目列表
        """
        if not project_scores:
            return []

        # 按总分降序排序
        sorted_scores = sorted(
            project_scores,
            key=lambda x: float(x['total_score']),
            reverse=True
        )

        # 分配排名（处理并列情况）
        for i, project in enumerate(sorted_scores):
            if i == 0:
                project['rank'] = 1
            else:
                prev_score = sorted_scores[i-1]['total_score']
                curr_score = project['total_score']
                if curr_score == prev_score:
                    project['rank'] = sorted_scores[i-1]['rank']
                else:
                    project['rank'] = i + 1

        return sorted_scores


class ScoringStatistics:
    """评分统计分析"""

    @staticmethod
    def calculate_dimension_statistics(scores: List[Decimal]) -> Dict:
        """
        计算维度的统计信息

        Args:
            scores: 分数列表

        Returns:
            {平均分, 最高分, 最低分, 中位数}
        """
        if not scores:
            return {
                'avg': Decimal('0'),
                'max': Decimal('0'),
                'min': Decimal('0'),
                'median': Decimal('0')
            }

        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        return {
            'avg': (sum(scores) / n).quantize(Decimal('0.01')),
            'max': max(scores),
            'min': min(scores),
            'median': (
                sorted_scores[n//2] if n % 2 == 1
                else (sorted_scores[n//2 - 1] + sorted_scores[n//2]) / 2
            ).quantize(Decimal('0.01'))
        }

    @staticmethod
    def calculate_grade_distribution(total_scores: List[Dict]) -> Dict[str, int]:
        """
        计算等级分布

        Args:
            total_scores: 项目总分列表

        Returns:
            {'excellent': 5, 'good': 10, ...}
        """
        distribution = {grade: 0 for grade in GRADING_STANDARDS.keys()}

        for score_record in total_scores:
            grade = score_record.get('grade', 'unqualified')
            distribution[grade] = distribution.get(grade, 0) + 1

        return distribution
