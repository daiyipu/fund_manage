"""
重新导入评分维度和指标数据
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.utils.database import get_db_connection

def insert_scoring_data():
    """插入评分维度和指标数据"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 插入评分维度
                print("插入评分维度...")
                dimensions = [
                    ('POLICY', '政策符合性指标', 60.00, 60.00, '评价项目与国家政策导向的符合程度', 1),
                    ('LAYOUT', '优化生产力布局指标', 30.00, 30.00, '评价项目对优化生产力布局的贡献', 2),
                    ('EXECUTION', '政策执行能力指标', 10.00, 10.00, '评价基金管理人的政策执行能力', 3)
                ]

                for dim in dimensions:
                    cursor.execute("""
                        INSERT INTO scoring_dimensions
                        (dimension_code, dimension_name, weight, max_score, description, display_order)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE dimension_name = VALUES(dimension_name)
                    """, dim)

                conn.commit()
                print(f"✓ 插入 {len(dimensions)} 个评分维度")

                # 获取维度ID
                cursor.execute("SELECT id, dimension_code FROM scoring_dimensions")
                dim_ids = {row['dimension_code']: row['id'] for row in cursor.fetchall()}

                # 插入政策符合性指标
                print("\n插入政策符合性指标...")
                policy_indicators = [
                    ('POLICY_01', dim_ids['POLICY'], '支持新质生产力发展情况', 16.67, 10.00, '评价项目在发展新质生产力方面的贡献程度', 1),
                    ('POLICY_02', dim_ids['POLICY'], '支持科技创新和促进成果转化情况', 16.67, 10.00, '评价项目在科技创新和成果转化方面的表现', 2),
                    ('POLICY_03', dim_ids['POLICY'], '推进全国统一大市场建设情况', 16.67, 10.00, '评价项目对统一大市场建设的促进作用', 3),
                    ('POLICY_04', dim_ids['POLICY'], '支持绿色发展情况', 8.33, 5.00, '评价项目在绿色发展和环保方面的贡献', 4),
                    ('POLICY_05', dim_ids['POLICY'], '支持民营经济发展和促进民间投资情况', 8.33, 5.00, '评价项目对民营经济发展的支持程度', 5),
                    ('POLICY_06', dim_ids['POLICY'], '壮大耐心资本情况', 8.33, 5.00, '评价项目对培育长期资本的作用', 6),
                    ('POLICY_07', dim_ids['POLICY'], '带动社会资本情况', 8.33, 5.00, '评价项目撬动社会资本的能力', 7),
                    ('POLICY_08', dim_ids['POLICY'], '服务社会民生等其他重点领域情况', 16.67, 10.00, '评价项目在民生等重点领域的贡献', 8),
                ]

                for ind in policy_indicators:
                    cursor.execute("""
                        INSERT INTO scoring_indicators
                        (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE indicator_name = VALUES(indicator_name)
                    """, ind)

                conn.commit()
                print(f"✓ 插入 {len(policy_indicators)} 个政策符合性指标")

                # 插入优化生产力布局指标
                print("\n插入优化生产力布局指标...")
                layout_indicators = [
                    ('LAYOUT_01', dim_ids['LAYOUT'], '落实国家区域战略情况', 33.33, 10.00, '评价项目对国家区域战略的落实程度', 1),
                    ('LAYOUT_02', dim_ids['LAYOUT'], '重点投向领域契合度', 33.33, 10.00, '评价项目投向与重点领域的契合程度', 2),
                    ('LAYOUT_03', dim_ids['LAYOUT'], '产能有效利用情况', 33.33, 10.00, '评价项目对产能有效利用的促进情况', 3),
                ]

                for ind in layout_indicators:
                    cursor.execute("""
                        INSERT INTO scoring_indicators
                        (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE indicator_name = VALUES(indicator_name)
                    """, ind)

                conn.commit()
                print(f"✓ 插入 {len(layout_indicators)} 个优化生产力布局指标")

                # 插入政策执行能力指标
                print("\n插入政策执行能力指标...")
                execution_indicators = [
                    ('EXEC_01', dim_ids['EXECUTION'], '资金效能情况', 40.00, 4.00, '评价资金使用的效率和效益', 1),
                    ('EXEC_02', dim_ids['EXECUTION'], '基金管理人专业水平', 60.00, 6.00, '评价基金管理人的专业能力和经验', 2),
                ]

                for ind in execution_indicators:
                    cursor.execute("""
                        INSERT INTO scoring_indicators
                        (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE indicator_name = VALUES(indicator_name)
                    """, ind)

                conn.commit()
                print(f"✓ 插入 {len(execution_indicators)} 个政策执行能力指标")

                print("\n" + "=" * 60)
                print("✓ 评分数据导入完成！")
                print(f"  - 3 个评分维度")
                print(f"  - 13 个评分指标")
                print("=" * 60)

                return True

    except Exception as e:
        print(f"错误: {str(e)}")
        return False

if __name__ == "__main__":
    insert_scoring_data()
