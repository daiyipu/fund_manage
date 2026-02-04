"""
检查数据库状态
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.utils.database import get_db_connection

try:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # 检查评分维度
            print("=== 检查评分维度 ===")
            cursor.execute("SELECT * FROM scoring_dimensions")
            dimensions = cursor.fetchall()
            print(f"评分维度数量: {len(dimensions)}")
            for dim in dimensions:
                print(f"  - {dim['dimension_code']}: {dim['dimension_name']}")

            print()

            # 检查评分指标
            print("=== 检查评分指标 ===")
            cursor.execute("SELECT * FROM scoring_indicators")
            indicators = cursor.fetchall()
            print(f"评分指标数量: {len(indicators)}")

            # 按维度分组统计
            from collections import defaultdict
            indicators_by_dim = defaultdict(list)
            for ind in indicators:
                indicators_by_dim[ind['dimension_id']].append(ind)

            for dim_id, inds in indicators_by_dim.items():
                cursor.execute("SELECT dimension_code FROM scoring_dimensions WHERE id = %s", (dim_id,))
                dim = cursor.fetchone()
                print(f"  - {dim['dimension_code'] if dim else dim_id}: {len(inds)} 个指标")

            print()

            # 检查项目
            print("=== 检查项目 ===")
            cursor.execute("SELECT COUNT(*) as count FROM projects")
            project_count = cursor.fetchone()
            print(f"项目数量: {project_count['count']}")

except Exception as e:
    print(f"错误: {str(e)}")
    print("\n请确保:")
    print("1. 数据库已创建 (python init_db.py)")
    print("2. .env 文件配置正确")
