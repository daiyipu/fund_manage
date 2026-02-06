"""
投资数据访问类
"""
from typing import List, Optional
from decimal import Decimal
import logging

from app.utils.database import get_db_connection

logger = logging.getLogger(__name__)


class InvestmentRepository:
    """投资数据访问类"""

    def create(self, investment: dict) -> int:
        """创建新投资"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO investments (
                            fund_id, investment_code, investment_name,
                            investment_amount, investment_date, industry,
                            investment_stage, description, status, created_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        investment['fund_id'], investment['investment_code'],
                        investment['investment_name'], investment.get('investment_amount'),
                        investment.get('investment_date'), investment.get('industry'),
                        investment.get('investment_stage', 'early'), investment.get('description'),
                        investment.get('status', 'draft'), investment['created_by']
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating investment: {str(e)}")
            raise

    def get_by_id(self, investment_id: int) -> Optional[dict]:
        """根据ID获取投资"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT i.*, u.real_name as creator_name,
                               f.fund_name, f.fund_code
                        FROM investments i
                        LEFT JOIN users u ON i.created_by = u.id
                        LEFT JOIN funds f ON i.fund_id = f.id
                        WHERE i.id = %s
                    """
                    cursor.execute(sql, (investment_id,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting investment by id: {str(e)}")
            raise

    def get_by_code(self, investment_code: str) -> Optional[dict]:
        """根据投资编码获取投资"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT i.*, u.real_name as creator_name,
                               f.fund_name, f.fund_code
                        FROM investments i
                        LEFT JOIN users u ON i.created_by = u.id
                        LEFT JOIN funds f ON i.fund_id = f.id
                        WHERE i.investment_code = %s
                    """
                    cursor.execute(sql, (investment_code,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting investment by code: {str(e)}")
            raise

    def list_investments(
        self,
        fund_id: Optional[int] = None,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """查询投资列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT i.*, u.real_name as creator_name,
                               f.fund_name, f.fund_code
                        FROM investments i
                        LEFT JOIN users u ON i.created_by = u.id
                        LEFT JOIN funds f ON i.fund_id = f.id
                        WHERE 1=1
                    """
                    params = []

                    if fund_id:
                        sql += " AND i.fund_id = %s"
                        params.append(fund_id)
                    if status:
                        sql += " AND i.status = %s"
                        params.append(status)
                    if industry:
                        sql += " AND i.industry = %s"
                        params.append(industry)

                    sql += " ORDER BY i.created_at DESC LIMIT %s"
                    params.append(limit)

                    cursor.execute(sql, tuple(params))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error listing investments: {str(e)}")
            raise

    def get_investments_for_scoring(self) -> List[dict]:
        """获取待评分投资列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT i.*, f.fund_name, f.fund_code
                        FROM investments i
                        LEFT JOIN funds f ON i.fund_id = f.id
                        WHERE i.status IN ('submitted', 'scoring')
                        ORDER BY i.created_at DESC
                    """
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting investments for scoring: {str(e)}")
            raise

    def update(self, investment_id: int, investment: dict) -> bool:
        """更新投资信息"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        UPDATE investments SET
                            investment_name = %s, investment_amount = %s,
                            investment_date = %s, industry = %s,
                            investment_stage = %s, description = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        investment['investment_name'], investment.get('investment_amount'),
                        investment.get('investment_date'), investment.get('industry'),
                        investment.get('investment_stage', 'early'), investment.get('description'),
                        investment_id
                    ))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating investment: {str(e)}")
            raise

    def update_status(self, investment_id: int, status: str) -> bool:
        """更新投资状态"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "UPDATE investments SET status = %s WHERE id = %s"
                    cursor.execute(sql, (status, investment_id))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating investment status: {str(e)}")
            raise

    def delete(self, investment_id: int) -> bool:
        """删除投资"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "DELETE FROM investments WHERE id = %s"
                    cursor.execute(sql, (investment_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting investment: {str(e)}")
            raise

    def count_investments(self, status: Optional[str] = None, fund_id: Optional[int] = None) -> int:
        """统计投资数量"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT COUNT(*) as count FROM investments WHERE 1=1"
                    params = []
                    if status:
                        sql += " AND status = %s"
                        params.append(status)
                    if fund_id:
                        sql += " AND fund_id = %s"
                        params.append(fund_id)
                    cursor.execute(sql, tuple(params))
                    result = cursor.fetchone()
                    return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting investments: {str(e)}")
            return 0

    def get_industries(self) -> List[str]:
        """获取所有行业列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT DISTINCT industry FROM investments WHERE industry IS NOT NULL ORDER BY industry"
                    cursor.execute(sql)
                    return [row['industry'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting industries: {str(e)}")
            return []
