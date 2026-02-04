"""
创建测试数据脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.services.project_service import ProjectService
from app.utils.database import get_db_connection


def create_test_projects():
    """创建测试项目"""
    print("创建测试项目...")

    project_service = ProjectService()

    # 获取admin用户ID
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = 'admin' LIMIT 1")
            result = cursor.fetchone()
            if not result:
                print("错误: 未找到admin用户，请先运行 python init_db.py")
                return
            admin_id = result['id']

    # 测试项目数据
    test_projects = [
        {
            'project_code': 'PRJ2024001',
            'project_name': '新能源汽车产业链投资基金',
            'fund_name': '国家绿色发展基金',
            'fund_manager': '华夏基金管理有限公司',
            'investment_amount': 50000.0,
            'investment_date': '2024-01-15',
            'region': '北京市',
            'industry': '新能源汽车',
            'project_stage': 'growth',
            'description': '投资于新能源汽车产业链上下游优质企业，支持电池、电机、电控等核心技术研发和产业化。',
            'status': 'submitted',
            'created_by': admin_id
        },
        {
            'project_code': 'PRJ2024002',
            'project_name': '人工智能创新基金',
            'fund_name': '中关村创业投资引导基金',
            'fund_manager': '中关村科技融资担保有限公司',
            'investment_amount': 30000.0,
            'investment_date': '2024-02-20',
            'region': '上海市',
            'industry': '人工智能',
            'project_stage': 'early',
            'description': '专注于人工智能基础层、技术层和应用层投资，重点支持计算机视觉、自然语言处理、机器学习等领域。',
            'status': 'submitted',
            'created_by': admin_id
        },
        {
            'project_code': 'PRJ2024003',
            'project_name': '生物医药产业发展基金',
            'fund_name': '国家集成电路产业投资基金',
            'fund_manager': '建信资本管理有限责任公司',
            'investment_amount': 80000.0,
            'investment_date': '2024-03-10',
            'region': '江苏省',
            'industry': '生物医药',
            'project_stage': 'growth',
            'description': '投资于创新药研发、高端医疗器械、精准医疗等细分领域，推动生物医药产业高质量发展。',
            'status': 'submitted',
            'created_by': admin_id
        },
        {
            'project_code': 'PRJ2024004',
            'project_name': '航空航天装备制造基金',
            'fund_name': '国家制造业转型升级基金',
            'fund_manager': '国投招商投资管理有限公司',
            'investment_amount': 100000.0,
            'investment_date': '2024-01-25',
            'region': '四川省',
            'industry': '航空航天',
            'project_stage': 'mature',
            'description': '支持民用航空、航天装备及关键零部件研发制造，促进航空航天产业自主可控发展。',
            'status': 'submitted',
            'created_by': admin_id
        },
        {
            'project_code': 'PRJ2024005',
            'project_name': '量子科技创业投资基金',
            'fund_name': '合肥市政府引导基金',
            'fund_manager': '合肥产投集团',
            'investment_amount': 20000.0,
            'investment_date': '2024-04-05',
            'region': '安徽省',
            'industry': '量子信息',
            'project_stage': 'seed',
            'description': '专注于量子计算、量子通信、量子测量等前沿领域的早期投资，培育量子科技产业集群。',
            'status': 'submitted',
            'created_by': admin_id
        }
    ]

    success_count = 0
    for project in test_projects:
        result = project_service.create_project(project)
        if result['success']:
            success_count += 1
            print(f"  ✓ 创建项目: {project['project_code']} - {project['project_name']}")
        else:
            print(f"  ✗ 创建失败: {project['project_code']} - {result['message']}")

    print(f"\n成功创建 {success_count}/{len(test_projects)} 个测试项目")
    return success_count > 0


def main():
    """主函数"""
    print("=" * 60)
    print("政府投资基金投向评分系统 - 创建测试数据")
    print("=" * 60)
    print()

    try:
        if create_test_projects():
            print()
            print("=" * 60)
            print("✓ 测试数据创建成功！")
            print()
            print("您现在可以:")
            print("1. 启动应用: python run.py")
            print("2. 访问: http://localhost:8501")
            print("3. 登录后进入'评分录入'页面进行评分")
            print("=" * 60)
        else:
            print("测试数据创建失败")
    except Exception as e:
        print(f"错误: {str(e)}")
        print("\n请确保:")
        print("1. 数据库已初始化 (python init_db.py)")
        print("2. .env 文件配置正确")
        sys.exit(1)


if __name__ == "__main__":
    main()
