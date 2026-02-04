"""
测试评分服务
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.repositories.scoring_repository import ScoringRepository
    from core.services.scoring_service import ScoringService

    print("✓ 模块导入成功")

    # 测试 ScoringRepository
    repo = ScoringRepository()
    print("✓ ScoringRepository 实例化成功")

    # 测试 get_all_dimensions
    dimensions = repo.get_all_dimensions()
    print(f"✓ 获取评分维度: {len(dimensions)} 个")

    # 测试 ScoringService
    service = ScoringService()
    print("✓ ScoringService 实例化成功")

    # 测试 get_scoring_structure
    structure = service.get_scoring_structure()
    print(f"✓ 获取评分结构: {len(structure)} 个维度")

    for dim_code, dim_data in structure.items():
        print(f"  - {dim_code}: {dim_data['name']} ({len(dim_data['indicators'])} 个指标)")

    print("\n所有测试通过！")

except Exception as e:
    print(f"❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
