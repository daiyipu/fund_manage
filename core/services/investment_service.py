"""
投资业务服务类
"""
from typing import Dict, List, Optional
from decimal import Decimal
import logging

from core.repositories.investment_repository import InvestmentRepository

logger = logging.getLogger(__name__)


class InvestmentService:
    """投资业务服务类"""

    def __init__(self):
        self.investment_repo = InvestmentRepository()

    def create_investment(self, investment: dict) -> Dict:
        """
        创建新投资

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # 检查投资编码是否已存在
            existing = self.investment_repo.get_by_code(investment['investment_code'])
            if existing:
                return {'success': False, 'message': '投资编码已存在'}

            investment_id = self.investment_repo.create(investment)
            logger.info(f"Created investment {investment_id}: {investment['investment_code']}")

            return {
                'success': True,
                'message': '投资创建成功',
                'data': {'investment_id': investment_id}
            }
        except Exception as e:
            logger.error(f"Error creating investment: {str(e)}")
            return {'success': False, 'message': f'创建失败: {str(e)}'}

    def get_investment(self, investment_id: int) -> Optional[dict]:
        """获取投资详情"""
        try:
            return self.investment_repo.get_by_id(investment_id)
        except Exception as e:
            logger.error(f"Error getting investment: {str(e)}")
            return None

    def list_investments(
        self,
        fund_id: Optional[int] = None,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """查询投资列表"""
        try:
            return self.investment_repo.list_investments(fund_id, status, industry, limit)
        except Exception as e:
            logger.error(f"Error listing investments: {str(e)}")
            return []

    def get_investments_for_scoring(self) -> List[dict]:
        """获取待评分投资列表"""
        try:
            return self.investment_repo.get_investments_for_scoring()
        except Exception as e:
            logger.error(f"Error getting investments for scoring: {str(e)}")
            return []

    def update_investment(self, investment_id: int, investment: dict) -> Dict:
        """
        更新投资信息

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.investment_repo.update(investment_id, investment)
            if success:
                logger.info(f"Updated investment {investment_id}")
                return {'success': True, 'message': '投资更新成功'}
            else:
                return {'success': False, 'message': '投资不存在'}
        except Exception as e:
            logger.error(f"Error updating investment: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    def delete_investment(self, investment_id: int) -> Dict:
        """
        删除投资

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.investment_repo.delete(investment_id)
            if success:
                logger.info(f"Deleted investment {investment_id}")
                return {'success': True, 'message': '投资删除成功'}
            else:
                return {'success': False, 'message': '投资不存在'}
        except Exception as e:
            logger.error(f"Error deleting investment: {str(e)}")
            return {'success': False, 'message': f'删除失败: {str(e)}'}

    def update_investment_status(self, investment_id: int, status: str) -> Dict:
        """
        更新投资状态

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            success = self.investment_repo.update_status(investment_id, status)
            if success:
                logger.info(f"Updated investment {investment_id} status to {status}")
                return {'success': True, 'message': '状态更新成功'}
            else:
                return {'success': False, 'message': '投资不存在'}
        except Exception as e:
            logger.error(f"Error updating investment status: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    def count_investments(
        self,
        status: Optional[str] = None,
        fund_id: Optional[int] = None
    ) -> int:
        """统计投资数量"""
        try:
            return self.investment_repo.count_investments(status, fund_id)
        except Exception as e:
            logger.error(f"Error counting investments: {str(e)}")
            return 0

    def count_scored_investments(self, fund_id: Optional[int] = None) -> int:
        """统计已评分投资数量"""
        try:
            return self.investment_repo.count_investments('completed', fund_id)
        except Exception as e:
            logger.error(f"Error counting scored investments: {str(e)}")
            return 0

    def get_industries(self) -> List[str]:
        """获取所有行业列表"""
        try:
            return self.investment_repo.get_industries()
        except Exception as e:
            logger.error(f"Error getting industries: {str(e)}")
            return []


# 创建全局实例
investment_service = InvestmentService()
