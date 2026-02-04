"""
项目数据访问类
"""
from typing import List, Optional
from decimal import Decimal
import logging

from app.utils.database import get_db_connection

logger = logging.getLogger(__name__)


class ProjectRepository:
    """项目数据访问类"""

    def create(self, project: dict) -> int:
        """创建新项目"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO projects (
                            project_code, project_name, fund_name, fund_manager,
                            investment_amount, investment_date, region, industry,
                            project_stage, description, status, created_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        project['project_code'], project['project_name'],
                        project.get('fund_name'), project.get('fund_manager'),
                        project.get('investment_amount'), project.get('investment_date'),
                        project.get('region'), project.get('industry'),
                        project.get('project_stage', 'early'), project.get('description'),
                        project.get('status', 'draft'), project['created_by']
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

    def get_by_id(self, project_id: int) -> Optional[dict]:
        """根据ID获取项目"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT p.*, u.real_name as creator_name
                        FROM projects p
                        LEFT JOIN users u ON p.created_by = u.id
                        WHERE p.id = %s
                    """
                    cursor.execute(sql, (project_id,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting project by id: {str(e)}")
            raise

    def get_by_code(self, project_code: str) -> Optional[dict]:
        """根据项目编码获取项目"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT p.*, u.real_name as creator_name
                        FROM projects p
                        LEFT JOIN users u ON p.created_by = u.id
                        WHERE p.project_code = %s
                    """
                    cursor.execute(sql, (project_code,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting project by code: {str(e)}")
            raise

    def list_projects(
        self,
        status: Optional[str] = None,
        region: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """查询项目列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT p.*, u.real_name as creator_name
                        FROM projects p
                        LEFT JOIN users u ON p.created_by = u.id
                        WHERE 1=1
                    """
                    params = []

                    if status:
                        sql += " AND p.status = %s"
                        params.append(status)
                    if region:
                        sql += " AND p.region = %s"
                        params.append(region)
                    if industry:
                        sql += " AND p.industry = %s"
                        params.append(industry)

                    sql += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
                    params.extend([limit, offset])

                    cursor.execute(sql, params)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            raise

    def get_projects_for_scoring(self) -> List[dict]:
        """获取待评分项目列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT p.*, u.real_name as creator_name
                        FROM projects p
                        LEFT JOIN users u ON p.created_by = u.id
                        WHERE p.status IN ('draft', 'submitted', 'scoring')
                        ORDER BY p.created_at DESC
                    """
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting projects for scoring: {str(e)}")
            raise

    def update(self, project_id: int, project: dict) -> bool:
        """更新项目"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        UPDATE projects SET
                            project_name = %s, fund_name = %s, fund_manager = %s,
                            investment_amount = %s, investment_date = %s,
                            region = %s, industry = %s, project_stage = %s,
                            description = %s, status = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        project['project_name'], project.get('fund_name'),
                        project.get('fund_manager'), project.get('investment_amount'),
                        project.get('investment_date'), project.get('region'),
                        project.get('industry'), project.get('project_stage'),
                        project.get('description'), project.get('status'),
                        project_id
                    ))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            raise

    def delete(self, project_id: int) -> bool:
        """删除项目"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "DELETE FROM projects WHERE id = %s"
                    cursor.execute(sql, (project_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            raise

    def update_status(self, project_id: int, status: str) -> bool:
        """更新项目状态"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "UPDATE projects SET status = %s WHERE id = %s"
                    cursor.execute(sql, (status, project_id))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating project status: {str(e)}")
            raise

    def count_projects(self, status: Optional[str] = None) -> int:
        """统计项目数量"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT COUNT(*) as count FROM projects WHERE 1=1"
                    params = []
                    if status:
                        sql += " AND status = %s"
                        params.append(status)
                    cursor.execute(sql, params)
                    result = cursor.fetchone()
                    return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting projects: {str(e)}")
            raise

    def get_regions(self) -> List[str]:
        """获取所有地区列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT DISTINCT region FROM projects WHERE region IS NOT NULL ORDER BY region"
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    return [r['region'] for r in results]
        except Exception as e:
            logger.error(f"Error getting regions: {str(e)}")
            raise

    def get_industries(self) -> List[str]:
        """获取所有行业列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT DISTINCT industry FROM projects WHERE industry IS NOT NULL ORDER BY industry"
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    return [i['industry'] for i in results]
        except Exception as e:
            logger.error(f"Error getting industries: {str(e)}")
            raise
