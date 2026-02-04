"""
项目业务服务类
"""
from typing import Dict, List, Optional
from decimal import Decimal
import logging

from core.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)


class ProjectService:
    """项目业务服务类"""

    def __init__(self):
        self.project_repo = ProjectRepository()

    def create_project(self, project: dict) -> Dict:
        """
        创建新项目

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # 检查项目编码是否已存在
            existing = self.project_repo.get_by_code(project['project_code'])
            if existing:
                return {'success': False, 'message': '项目编码已存在'}

            project_id = self.project_repo.create(project)
            logger.info(f"Created project {project_id}: {project['project_code']}")

            return {
                'success': True,
                'message': '项目创建成功',
                'data': {'project_id': project_id}
            }
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return {'success': False, 'message': f'创建失败: {str(e)}'}

    def get_project(self, project_id: int) -> Optional[dict]:
        """获取项目详情"""
        try:
            return self.project_repo.get_by_id(project_id)
        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            return None

    def list_projects(
        self,
        status: Optional[str] = None,
        region: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """查询项目列表"""
        try:
            return self.project_repo.list_projects(status, region, industry, limit)
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return []

    def get_projects_for_scoring(self) -> List[dict]:
        """获取待评分项目列表"""
        try:
            return self.project_repo.get_projects_for_scoring()
        except Exception as e:
            logger.error(f"Error getting projects for scoring: {str(e)}")
            return []

    def update_project(self, project_id: int, project: dict) -> Dict:
        """
        更新项目信息

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.project_repo.update(project_id, project)
            if success:
                logger.info(f"Updated project {project_id}")
                return {'success': True, 'message': '项目更新成功'}
            else:
                return {'success': False, 'message': '项目不存在'}
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    def delete_project(self, project_id: int) -> Dict:
        """
        删除项目

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.project_repo.delete(project_id)
            if success:
                logger.info(f"Deleted project {project_id}")
                return {'success': True, 'message': '项目删除成功'}
            else:
                return {'success': False, 'message': '项目不存在'}
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return {'success': False, 'message': f'删除失败: {str(e)}'}

    def update_project_status(self, project_id: int, status: str) -> Dict:
        """
        更新项目状态

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.project_repo.update_status(project_id, status)
            if success:
                logger.info(f"Updated project {project_id} status to {status}")
                return {'success': True, 'message': '状态更新成功'}
            else:
                return {'success': False, 'message': '项目不存在'}
        except Exception as e:
            logger.error(f"Error updating project status: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    def count_projects(self, status: Optional[str] = None) -> int:
        """统计项目数量"""
        try:
            return self.project_repo.count_projects(status)
        except Exception as e:
            logger.error(f"Error counting projects: {str(e)}")
            return 0

    def count_scored_projects(self) -> int:
        """统计已评分项目数量"""
        try:
            return self.project_repo.count_projects('completed')
        except Exception as e:
            logger.error(f"Error counting scored projects: {str(e)}")
            return 0

    def get_regions(self) -> List[str]:
        """获取所有地区列表"""
        try:
            return self.project_repo.get_regions()
        except Exception as e:
            logger.error(f"Error getting regions: {str(e)}")
            return []

    def get_industries(self) -> List[str]:
        """获取所有行业列表"""
        try:
            return self.project_repo.get_industries()
        except Exception as e:
            logger.error(f"Error getting industries: {str(e)}")
            return []
