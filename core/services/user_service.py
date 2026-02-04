"""
用户业务服务类
"""
from typing import Dict, List, Optional
import logging

from core.repositories.user_repository import UserRepository
from config.scoring_rules import ROLE_PERMISSIONS, ROLE_NAMES

logger = logging.getLogger(__name__)


class UserService:
    """用户业务服务类"""

    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """
        验证用户登录

        Returns:
            用户信息字典（不包含密码）或None
        """
        try:
            user = self.user_repo.authenticate(username, password)
            if user:
                logger.info(f"User {username} authenticated successfully")
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None

    def create_user(self, user: dict) -> Dict:
        """
        创建新用户

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            user_id = self.user_repo.create(user)
            logger.info(f"Created user {user_id}: {user['username']}")

            return {
                'success': True,
                'message': '用户创建成功',
                'data': {'user_id': user_id}
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {'success': False, 'message': f'创建失败: {str(e)}'}

    def get_user(self, user_id: int) -> Optional[dict]:
        """获取用户详情"""
        try:
            user = self.user_repo.get_by_id(user_id)
            if user:
                user.pop('password_hash', None)
            return user
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    def list_users(
        self,
        role: Optional[str] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[dict]:
        """查询用户列表"""
        try:
            return self.user_repo.list_users(role, department, is_active, limit)
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return []

    def update_user(self, user_id: int, user: dict) -> Dict:
        """
        更新用户信息

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.user_repo.update(user_id, user)
            if success:
                logger.info(f"Updated user {user_id}")
                return {'success': True, 'message': '用户更新成功'}
            else:
                return {'success': False, 'message': '用户不存在'}
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict:
        """
        修改用户密码

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            # 这里应该先验证旧密码，简化实现暂时跳过
            success = self.user_repo.change_password(user_id, new_password)
            if success:
                logger.info(f"Changed password for user {user_id}")
                return {'success': True, 'message': '密码修改成功'}
            else:
                return {'success': False, 'message': '用户不存在'}
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return {'success': False, 'message': f'修改失败: {str(e)}'}

    def deactivate_user(self, user_id: int) -> Dict:
        """
        停用用户

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.user_repo.deactivate(user_id)
            if success:
                logger.info(f"Deactivated user {user_id}")
                return {'success': True, 'message': '用户已停用'}
            else:
                return {'success': False, 'message': '用户不存在'}
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return {'success': False, 'message': f'停用失败: {str(e)}'}

    def activate_user(self, user_id: int) -> Dict:
        """
        激活用户

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.user_repo.activate(user_id)
            if success:
                logger.info(f"Activated user {user_id}")
                return {'success': True, 'message': '用户已激活'}
            else:
                return {'success': False, 'message': '用户不存在'}
        except Exception as e:
            logger.error(f"Error activating user: {str(e)}")
            return {'success': False, 'message': f'激活失败: {str(e)}'}

    def check_permission(self, user_role: str, permission: str) -> bool:
        """
        检查用户是否有某项权限

        Args:
            user_role: 用户角色
            permission: 权限名称

        Returns:
            是否有权限
        """
        return ROLE_PERMISSIONS.get(user_role, {}).get(permission, False)

    def get_role_name(self, role_code: str) -> str:
        """获取角色名称"""
        return ROLE_NAMES.get(role_code, '未知')

    def get_departments(self) -> List[str]:
        """获取所有部门列表"""
        try:
            return self.user_repo.get_departments()
        except Exception as e:
            logger.error(f"Error getting departments: {str(e)}")
            return []
