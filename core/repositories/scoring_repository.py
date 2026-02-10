"""
评分数据访问类
"""
from typing import List, Optional, Dict
from decimal import Decimal
import logging

from app.utils.database import get_db_connection

logger = logging.getLogger(__name__)


class ScoringRepository:
    """评分数据访问类"""

    def get_all_dimensions(self) -> List[Dict]:
        """获取所有评分维度"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT * FROM scoring_dimensions
                        WHERE is_active = TRUE
                        ORDER BY display_order
                    """
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting dimensions: {str(e)}")
            raise

    def get_indicators_by_dimension(self, dimension_id: int) -> List[Dict]:
        """获取维度的所有指标"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT * FROM scoring_indicators
                        WHERE dimension_id = %s AND is_active = TRUE
                        ORDER BY display_order
                    """
                    cursor.execute(sql, (dimension_id,))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting indicators: {str(e)}")
            raise

    def get_dimension_by_code(self, dimension_code: str) -> Optional[Dict]:
        """根据维度代码获取维度信息"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT * FROM scoring_dimensions
                        WHERE dimension_code = %s AND is_active = TRUE
                    """
                    cursor.execute(sql, (dimension_code,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting dimension by code: {str(e)}")
            raise

    def get_indicator_by_code(self, indicator_code: str) -> Optional[Dict]:
        """根据指标代码获取指标信息"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT si.*, sd.dimension_code
                        FROM scoring_indicators si
                        JOIN scoring_dimensions sd ON si.dimension_id = sd.id
                        WHERE si.indicator_code = %s AND si.is_active = TRUE
                    """
                    cursor.execute(sql, (indicator_code,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting indicator by code: {str(e)}")
            raise

    def save_score(
        self,
        project_id: int,
        dimension_id: int,
        indicator_id: int,
        score: Decimal,
        weighted_score: Decimal,
        scorer_id: int,
        scorer_comment: Optional[str] = None
    ) -> int:
        """保存单个指标评分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO project_scores
                        (project_id, dimension_id, indicator_id, score, weighted_score,
                         scorer_id, scorer_comment)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        score = VALUES(score),
                        weighted_score = VALUES(weighted_score),
                        scorer_id = VALUES(scorer_id),
                        scorer_comment = VALUES(scorer_comment),
                        scored_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(sql, (
                        project_id, dimension_id, indicator_id, score, weighted_score,
                        scorer_id, scorer_comment
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving score: {str(e)}")
            raise

    def get_project_scores(self, project_id: int) -> List[Dict]:
        """获取项目的所有评分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT ps.*, si.indicator_code, si.indicator_name,
                               sd.dimension_code, sd.dimension_name,
                               u.real_name as scorer_name
                        FROM project_scores ps
                        JOIN scoring_indicators si ON ps.indicator_id = si.id
                        JOIN scoring_dimensions sd ON ps.dimension_id = sd.id
                        LEFT JOIN users u ON ps.scorer_id = u.id
                        WHERE ps.project_id = %s
                        ORDER BY sd.display_order, si.display_order
                    """
                    cursor.execute(sql, (project_id,))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting project scores: {str(e)}")
            raise

    def save_dimension_summary(
        self,
        project_id: int,
        dimension_id: int,
        total_score: Decimal,
        weighted_total: Decimal
    ) -> int:
        """保存维度汇总"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO scoring_summaries
                        (project_id, dimension_id, total_score, weighted_total)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        total_score = VALUES(total_score),
                        weighted_total = VALUES(weighted_total),
                        calculated_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(sql, (project_id, dimension_id, total_score, weighted_total))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving dimension summary: {str(e)}")
            raise

    def get_dimension_summaries(self, project_id: int) -> List[Dict]:
        """获取项目的所有维度汇总"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT ss.*, sd.dimension_code, sd.dimension_name
                        FROM scoring_summaries ss
                        JOIN scoring_dimensions sd ON ss.dimension_id = sd.id
                        WHERE ss.project_id = %s
                        ORDER BY sd.display_order
                    """
                    cursor.execute(sql, (project_id,))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting dimension summaries: {str(e)}")
            raise

    def save_project_total(
        self,
        project_id: int,
        total_score: Decimal,
        policy_score: Decimal,
        layout_score: Decimal,
        execution_score: Decimal,
        grade: str,
        reviewed_by: Optional[int] = None,
        review_comment: Optional[str] = None
    ) -> int:
        """保存项目总分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO project_total_scores
                        (project_id, total_score, policy_score, layout_score,
                         execution_score, grade, reviewed_by, review_comment)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        total_score = VALUES(total_score),
                        policy_score = VALUES(policy_score),
                        layout_score = VALUES(layout_score),
                        execution_score = VALUES(execution_score),
                        grade = VALUES(grade),
                        reviewed_by = VALUES(reviewed_by),
                        review_comment = VALUES(review_comment),
                        reviewed_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(sql, (
                        project_id, total_score, policy_score, layout_score,
                        execution_score, grade, reviewed_by, review_comment
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving project total: {str(e)}")
            raise

    def get_project_total_score(self, project_id: int) -> Optional[Dict]:
        """获取项目总分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT pts.*, u.real_name as reviewer_name
                        FROM project_total_scores pts
                        LEFT JOIN users u ON pts.reviewed_by = u.id
                        WHERE pts.project_id = %s
                    """
                    cursor.execute(sql, (project_id,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting project total score: {str(e)}")
            raise

    def get_all_project_totals(self) -> List[Dict]:
        """获取所有项目总分（用于排名）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT pts.*, p.project_code, p.project_name, p.region, p.industry
                        FROM project_total_scores pts
                        JOIN projects p ON pts.project_id = p.id
                        ORDER BY pts.total_score DESC
                    """
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting all project totals: {str(e)}")
            raise

    def update_project_rankings(self, rankings: List[Dict]):
        """批量更新项目排名"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "UPDATE project_total_scores SET rank_in_period = %s WHERE project_id = %s"
                    for item in rankings:
                        cursor.execute(sql, (item['rank'], item['project_id']))
                    conn.commit()
                    logger.info(f"Updated {len(rankings)} project rankings")
        except Exception as e:
            logger.error(f"Error updating rankings: {str(e)}")
            raise

    # ==================== Investment 相关方法 ====================

    def save_fund_score(
        self,
        fund_id: int,
        dimension_id: int,
        indicator_id: int,
        score: Decimal,
        weighted_score: Decimal,
        scorer_id: int,
        scorer_comment: Optional[str] = None
    ) -> int:
        """保存投资的单个指标评分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO fund_scores
                        (fund_id, dimension_id, indicator_id, score, weighted_score,
                         scorer_id, scorer_comment)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        score = VALUES(score),
                        weighted_score = VALUES(weighted_score),
                        scorer_id = VALUES(scorer_id),
                        scorer_comment = VALUES(scorer_comment),
                        scored_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(sql, (
                        fund_id, dimension_id, indicator_id, score, weighted_score,
                        scorer_id, scorer_comment
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving investment score: {str(e)}")
            raise

    def get_fund_scores(self, fund_id: int) -> List[Dict]:
        """获取投资的所有评分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT ins.*, si.indicator_code, si.indicator_name,
                               sd.dimension_code, sd.dimension_name,
                               u.real_name as scorer_name
                        FROM fund_scores ins
                        JOIN scoring_indicators si ON ins.indicator_id = si.id
                        JOIN scoring_dimensions sd ON ins.dimension_id = sd.id
                        LEFT JOIN users u ON ins.scorer_id = u.id
                        WHERE ins.fund_id = %s
                        ORDER BY sd.display_order, si.display_order
                    """
                    cursor.execute(sql, (fund_id,))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting investment scores: {str(e)}")
            raise

    def save_fund_dimension_summary(
        self,
        fund_id: int,
        dimension_id: int,
        total_score: Decimal,
        weighted_total: Decimal
    ) -> int:
        """保存投资的维度汇总"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO fund_scoring_summary
                        (fund_id, dimension_id, total_score, weighted_total)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        total_score = VALUES(total_score),
                        weighted_total = VALUES(weighted_total),
                        calculated_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(sql, (fund_id, dimension_id, total_score, weighted_total))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving investment dimension summary: {str(e)}")
            raise

    def save_fund_total(
        self,
        fund_id: int,
        total_score: Decimal,
        policy_score: Decimal,
        layout_score: Decimal,
        execution_score: Decimal,
        grade: str,
        reviewed_by: Optional[int] = None,
        review_comment: Optional[str] = None
    ) -> int:
        """保存投资总分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO fund_total_scores
                        (fund_id, total_score, policy_score, layout_score,
                         execution_score, grade, reviewed_by, review_comment)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        total_score = VALUES(total_score),
                        policy_score = VALUES(policy_score),
                        layout_score = VALUES(layout_score),
                        execution_score = VALUES(execution_score),
                        grade = VALUES(grade),
                        reviewed_by = VALUES(reviewed_by),
                        review_comment = VALUES(review_comment),
                        reviewed_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(sql, (
                        fund_id, total_score, policy_score, layout_score,
                        execution_score, grade, reviewed_by, review_comment
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving investment total: {str(e)}")
            raise

    def get_fund_total_score(self, fund_id: int) -> Optional[Dict]:
        """获取投资总分"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT its.*, u.real_name as reviewer_name
                        FROM fund_total_scores its
                        LEFT JOIN users u ON its.reviewed_by = u.id
                        WHERE its.fund_id = %s
                    """
                    cursor.execute(sql, (fund_id,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting investment total score: {str(e)}")
            raise

    def get_all_fund_totals(self) -> List[Dict]:
        """获取所有基金总分（用于排名）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT its.*, f.fund_code, f.fund_name, f.region
                        FROM fund_total_scores its
                        JOIN funds f ON its.fund_id = f.id
                        ORDER BY its.total_score DESC
                    """
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting all fund totals: {str(e)}")
            raise

    def update_fund_rankings(self, rankings: List[Dict]):
        """批量更新投资排名"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "UPDATE fund_total_scores SET rank_in_period = %s WHERE fund_id = %s"
                    for item in rankings:
                        cursor.execute(sql, (item['rank'], item['fund_id']))
                    conn.commit()
                    logger.info(f"Updated {len(rankings)} investment rankings")
        except Exception as e:
            logger.error(f"Error updating investment rankings: {str(e)}")
            raise
