"""
基金业务服务类
"""
from typing import Dict, List, Optional
from decimal import Decimal
import logging

from core.repositories.fund_repository import FundRepository

logger = logging.getLogger(__name__)


class FundService:
    """基金业务服务类"""

    def __init__(self):
        self.fund_repo = FundRepository()

    def create_fund(self, fund: dict) -> Dict:
        """
        创建新基金

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # 检查基金编码是否已存在
            existing = self.fund_repo.get_by_code(fund['fund_code'])
            if existing:
                return {'success': False, 'message': '基金编码已存在'}

            fund_id = self.fund_repo.create(fund)
            logger.info(f"Created fund {fund_id}: {fund['fund_code']}")

            return {
                'success': True,
                'message': '基金创建成功',
                'data': {'fund_id': fund_id}
            }
        except Exception as e:
            logger.error(f"Error creating fund: {str(e)}")
            return {'success': False, 'message': f'创建失败: {str(e)}'}

    def get_fund(self, fund_id: int) -> Optional[dict]:
        """获取基金详情"""
        try:
            return self.fund_repo.get_by_id(fund_id)
        except Exception as e:
            logger.error(f"Error getting fund: {str(e)}")
            return None

    def list_funds(
        self,
        status: Optional[str] = None,
        region: Optional[str] = None,
        fund_type: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """查询基金列表"""
        try:
            return self.fund_repo.list_funds(status, region, fund_type, limit)
        except Exception as e:
            logger.error(f"Error listing funds: {str(e)}")
            return []

    def update_fund(self, fund_id: int, fund: dict) -> Dict:
        """
        更新基金信息

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.fund_repo.update(fund_id, fund)
            if success:
                logger.info(f"Updated fund {fund_id}")
                return {'success': True, 'message': '基金更新成功'}
            else:
                return {'success': False, 'message': '基金不存在'}
        except Exception as e:
            logger.error(f"Error updating fund: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    def delete_fund(self, fund_id: int) -> Dict:
        """
        删除基金

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.fund_repo.delete(fund_id)
            if success:
                logger.info(f"Deleted fund {fund_id}")
                return {'success': True, 'message': '基金删除成功'}
            else:
                return {'success': False, 'message': '基金不存在'}
        except Exception as e:
            logger.error(f"Error deleting fund: {str(e)}")
            return {'success': False, 'message': f'删除失败: {str(e)}'}

    def update_fund_status(self, fund_id: int, status: str) -> Dict:
        """
        更新基金状态

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.fund_repo.update_status(fund_id, status)
            if success:
                logger.info(f"Updated fund {fund_id} status to {status}")
                return {'success': True, 'message': '状态更新成功'}
            else:
                return {'success': False, 'message': '基金不存在'}
        except Exception as e:
            logger.error(f"Error updating fund status: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    def count_funds(self, status: Optional[str] = None) -> int:
        """统计基金数量"""
        try:
            return self.fund_repo.count_funds(status)
        except Exception as e:
            logger.error(f"Error counting funds: {str(e)}")
            return 0

    def get_fund_investments(self, fund_id: int) -> List[dict]:
        """获取基金下的所有投资"""
        try:
            return self.fund_repo.get_fund_investments(fund_id)
        except Exception as e:
            logger.error(f"Error getting fund investments: {str(e)}")
            return []

    def get_regions(self) -> List[str]:
        """获取所有地区列表"""
        try:
            return self.fund_repo.get_regions()
        except Exception as e:
            logger.error(f"Error getting regions: {str(e)}")
            return []

    def get_fund_types(self) -> List[str]:
        """获取所有基金类型列表"""
        try:
            return self.fund_repo.get_fund_types()
        except Exception as e:
            logger.error(f"Error getting fund types: {str(e)}")
            return []


# 创建全局实例
fund_service = FundService()
