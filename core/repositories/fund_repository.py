"""
基金数据访问类
"""
from typing import List, Optional
from decimal import Decimal
import logging

from app.utils.database import get_db_connection

logger = logging.getLogger(__name__)


class FundRepository:
    """基金数据访问类"""

    def create(self, fund: dict) -> int:
        """创建新基金"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO funds (
                            fund_code, fund_name, fund_manager, total_amount,
                            establishment_date, fund_type, region, department,
                            description, status, created_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        fund['fund_code'], fund['fund_name'], fund['fund_manager'],
                        fund.get('total_amount'), fund.get('establishment_date'),
                        fund.get('fund_type'), fund.get('region'), fund.get('department'),
                        fund.get('description'), fund.get('status', 'draft'), fund['created_by']
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating fund: {str(e)}")
            raise

    def get_by_id(self, fund_id: int) -> Optional[dict]:
        """根据ID获取基金"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT f.*, u.real_name as creator_name
                        FROM funds f
                        LEFT JOIN users u ON f.created_by = u.id
                        WHERE f.id = %s
                    """
                    cursor.execute(sql, (fund_id,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting fund by id: {str(e)}")
            raise

    def get_by_code(self, fund_code: str) -> Optional[dict]:
        """根据基金编码获取基金"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT f.*, u.real_name as creator_name
                        FROM funds f
                        LEFT JOIN users u ON f.created_by = u.id
                        WHERE f.fund_code = %s
                    """
                    cursor.execute(sql, (fund_code,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting fund by code: {str(e)}")
            raise

    def list_funds(
        self,
        status: Optional[str] = None,
        region: Optional[str] = None,
        fund_type: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """查询基金列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT f.*, u.real_name as creator_name
                        FROM funds f
                        LEFT JOIN users u ON f.created_by = u.id
                        WHERE 1=1
                    """
                    params = []

                    if status:
                        sql += " AND f.status = %s"
                        params.append(status)
                    if region:
                        sql += " AND f.region = %s"
                        params.append(region)
                    if fund_type:
                        sql += " AND f.fund_type = %s"
                        params.append(fund_type)

                    sql += " ORDER BY f.created_at DESC LIMIT %s"
                    params.append(limit)

                    cursor.execute(sql, tuple(params))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error listing funds: {str(e)}")
            raise

    def update(self, fund_id: int, fund: dict) -> bool:
        """更新基金信息"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        UPDATE funds SET
                            fund_name = %s, fund_manager = %s, total_amount = %s,
                            establishment_date = %s, fund_type = %s, region = %s,
                            department = %s, description = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        fund['fund_name'], fund['fund_manager'], fund.get('total_amount'),
                        fund.get('establishment_date'), fund.get('fund_type'),
                        fund.get('region'), fund.get('department'), fund.get('description'),
                        fund_id
                    ))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating fund: {str(e)}")
            raise

    def update_status(self, fund_id: int, status: str) -> bool:
        """更新基金状态"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "UPDATE funds SET status = %s WHERE id = %s"
                    cursor.execute(sql, (status, fund_id))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating fund status: {str(e)}")
            raise

    def delete(self, fund_id: int) -> bool:
        """删除基金"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "DELETE FROM funds WHERE id = %s"
                    cursor.execute(sql, (fund_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting fund: {str(e)}")
            raise

    def count_funds(self, status: Optional[str] = None) -> int:
        """统计基金数量"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT COUNT(*) as count FROM funds"
                    if status:
                        sql += " WHERE status = %s"
                        cursor.execute(sql, (status,))
                    else:
                        cursor.execute(sql)
                    result = cursor.fetchone()
                    return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting funds: {str(e)}")
            return 0

    def get_regions(self) -> List[str]:
        """获取所有地区列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT DISTINCT region FROM funds WHERE region IS NOT NULL ORDER BY region"
                    cursor.execute(sql)
                    return [row['region'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting regions: {str(e)}")
            return []

    def get_fund_types(self) -> List[str]:
        """获取所有基金类型列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT DISTINCT fund_type FROM funds WHERE fund_type IS NOT NULL ORDER BY fund_type"
                    cursor.execute(sql)
                    return [row['fund_type'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting fund types: {str(e)}")
            return []

    def get_fund_investments(self, fund_id: int) -> List[dict]:
        """获取基金下的所有投资"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT i.*, u.real_name as creator_name
                        FROM investments i
                        LEFT JOIN users u ON i.created_by = u.id
                        WHERE i.fund_id = %s
                        ORDER BY i.created_at DESC
                    """
                    cursor.execute(sql, (fund_id,))
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting fund investments: {str(e)}")
            raise
