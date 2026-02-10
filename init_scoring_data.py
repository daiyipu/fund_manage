#!/usr/bin/env python3
"""
初始化评分维度和指标数据（简化版）
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import get_db_connection


def init_scoring_data():
    """初始化评分维度和指标数据"""
    try:
        print("开始初始化评分数据...")

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 获取dimension_id映射
                cursor.execute('SELECT id, dimension_code FROM scoring_dimensions')
                dim_map = {row['dimension_code']: row['id'] for row in cursor.fetchall()}
                print(f"Dimension ID映射: {dim_map}")

                # 清空现有数据
                print("\n清空现有评分数据...")
                cursor.execute("DELETE FROM fund_scores")
                cursor.execute("DELETE FROM fund_scoring_summary")
                cursor.execute("DELETE FROM fund_total_scores")
                cursor.execute("DELETE FROM scoring_indicators")
                cursor.execute("DELETE FROM scoring_dimensions")
                conn.commit()
                print("✓ 清空完成")

                # 插入评分维度
                print("\n插入评分维度...")
                dimensions_sql = """
                    INSERT INTO scoring_dimensions (dimension_code, dimension_name, weight, max_score, description, display_order)
                    VALUES
                    ('POLICY', '政策符合性指标', 60.00, 60.00, '评价项目与国家政策导向的符合程度', 1),
                    ('LAYOUT', '优化生产力布局指标', 30.00, 30.00, '评价项目对优化生产力布局的贡献', 2),
                    ('EXECUTION', '政策执行能力指标', 10.00, 10.00, '评价基金管理人的政策执行能力', 3)
                """
                cursor.execute(dimensions_sql)
                conn.commit()
                print("✓ 插入了 3 个维度")

                # 重新获取dimension_id
                cursor.execute('SELECT id, dimension_code FROM scoring_dimensions')
                dim_map = {row['dimension_code']: row['id'] for row in cursor.fetchall()}

                # ============== 政策符合性指标 (14个叶子指标) ==============
                print("\n插入政策符合性指标...")

                # 叶子指标 (4个)
                policy_leaf = [
                    ('POLICY_01', '支持新质生产力发展情况', 16.67, 10.00, 1),
                    ('POLICY_05', '支持民营经济发展和促进民间投资情况', 8.33, 5.00, 5),
                    ('POLICY_06', '壮大耐心资本情况', 8.33, 5.00, 6),
                    ('POLICY_07', '带动社会资本情况', 8.33, 5.00, 7),
                ]
                for code, name, weight, max_score, order in policy_leaf:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, 'leaf', 0)"
                    cursor.execute(sql, (code, dim_map['POLICY'], name, weight, max_score, f'{name}评分标准', order))

                # 父指标 (4个)
                policy_parent = [
                    ('POLICY_02', '支持科技创新和促进成果转化情况', 16.67, 10.00, 2),
                    ('POLICY_03', '推进全国统一大市场建设情况', 16.67, 10.00, 3),
                    ('POLICY_04', '支持绿色发展情况', 8.33, 5.00, 4),
                    ('POLICY_08', '服务社会民生等其他重点领域情况', 16.67, 10.00, 8),
                ]
                for code, name, weight, max_score, order in policy_parent:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, 'parent', 0)"
                    cursor.execute(sql, (code, dim_map['POLICY'], name, weight, max_score, f'{name}评分标准', order))

                conn.commit()

                # 获取父指标ID
                parent_ids = {}
                for code in ['POLICY_02', 'POLICY_03', 'POLICY_04', 'POLICY_08']:
                    cursor.execute("SELECT id FROM scoring_indicators WHERE indicator_code = %s", (code,))
                    parent_ids[code] = cursor.fetchone()['id']

                # POLICY_02 子指标 (3个)
                print("  插入POLICY_02子指标...")
                policy_02_subs = [
                    ('POLICY_02_01', '新增发明专利或技术成果', 30.0, 3.0, 21, '新增6项及以上=3分，新增5项=2.5分，新增4项=2分，新增3项=1.5分，新增2项=1分，新增1项=0.5分，无新增=0分'),
                    ('POLICY_02_02', '支持科技成果转化', 20.0, 2.0, 22, '支持科技成果转化=2分，无科技成果转化=0分'),
                    ('POLICY_02_03', '支持解决"卡脖子"难题', 50.0, 5.0, 23, '支持多个"卡脖子"领域=5分，支持一个"卡脖子"领域=3分，不涉及"卡脖子"技术=0分'),
                ]
                for code, name, weight, max_score, order, criteria in policy_02_subs:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'leaf', 1)"
                    cursor.execute(sql, (code, dim_map['POLICY'], name, weight, max_score, criteria, order, parent_ids['POLICY_02']))

                # POLICY_03 子指标 (3个)
                print("  插入POLICY_03子指标...")
                policy_03_subs = [
                    ('POLICY_03_01', '返投比例情况', 30.0, 3.0, 31, '未设置返投要求或<50%%=3分，50%%-100%%=2分，100%%-150%%=1分，≥150%%=0分'),
                    ('POLICY_03_02', '注册地迁移条件', 30.0, 3.0, 32, '未设置注册地迁移条件=3分，设置了注册地迁移条件=0分'),
                    ('POLICY_03_03', '违规行为情况', 40.0, 4.0, 33, '不存在违规行为=4分，存在违规行为=0分'),
                ]
                for code, name, weight, max_score, order, criteria in policy_03_subs:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'leaf', 1)"
                    cursor.execute(sql, (code, dim_map['POLICY'], name, weight, max_score, criteria, order, parent_ids['POLICY_03']))

                # POLICY_04 子指标 (2个)
                print("  插入POLICY_04子指标...")
                policy_04_subs = [
                    ('POLICY_04_01', '碳减排比例', 60.0, 3.0, 41, '≥5%%=3分，3%%-5%%=2分，1%%-3%%=1分，<1%%或负数=0分'),
                    ('POLICY_04_02', '绿色发展投向比例', 40.0, 2.0, 42, '投向比例>20%%=2分，投向比例≤20%%=1分，不涉及绿色发展领域=0分'),
                ]
                for code, name, weight, max_score, order, criteria in policy_04_subs:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'leaf', 1)"
                    cursor.execute(sql, (code, dim_map['POLICY'], name, weight, max_score, criteria, order, parent_ids['POLICY_04']))

                # POLICY_08 子指标 (2个)
                print("  插入POLICY_08子指标...")
                policy_08_subs = [
                    ('POLICY_08_01', '就业/税收/营收排名', 50.0, 5.0, 81, '前10%%=5分，前10%%-30%%=4分，30%%-50%%=3分，50%%-70%%=2分，70%%-90%%=1分，90%%以后=0分'),
                    ('POLICY_08_02', '重点领域贡献情况', 50.0, 5.0, 82, '涉及两个及以上重点领域=5分，涉及一个重点领域=3分，不涉及重点领域=0分'),
                ]
                for code, name, weight, max_score, order, criteria in policy_08_subs:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'leaf', 1)"
                    cursor.execute(sql, (code, dim_map['POLICY'], name, weight, max_score, criteria, order, parent_ids['POLICY_08']))

                conn.commit()
                print("✓ 政策符合性指标完成 (14个)")

                # ============== 优化生产力布局指标 (4个叶子指标) ==============
                print("\n插入优化生产力布局指标...")

                layout_leaf = [
                    ('LAYOUT_01', '落实国家区域战略情况', 33.33, 10.00, 1),
                    ('LAYOUT_02', '重点投向领域契合度', 33.33, 10.00, 2),
                ]
                for code, name, weight, max_score, order in layout_leaf:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, 'leaf', 0)"
                    cursor.execute(sql, (code, dim_map['LAYOUT'], name, weight, max_score, f'{name}评分标准', order))

                layout_parent = [
                    ('LAYOUT_03', '产能有效利用情况', 33.33, 10.00, 3),
                ]
                for code, name, weight, max_score, order in layout_parent:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, 'parent', 0)"
                    cursor.execute(sql, (code, dim_map['LAYOUT'], name, weight, max_score, f'{name}评分标准', order))

                conn.commit()

                cursor.execute("SELECT id FROM scoring_indicators WHERE indicator_code = 'LAYOUT_03'")
                layout_03_id = cursor.fetchone()['id']

                # LAYOUT_03 子指标 (2个)
                print("  插入LAYOUT_03子指标...")
                layout_03_subs = [
                    ('LAYOUT_03_01', '产能利用率', 50.0, 5.0, 31, '高于行业平均水平=5分，接近平均水平±5%%=3分，低于平均水平=0分'),
                    ('LAYOUT_03_02', '资产周转率', 50.0, 5.0, 32, '≥100%%=5分，80%%-100%%=4分，60%%-80%%=3分，<60%%=0分'),
                ]
                for code, name, weight, max_score, order, criteria in layout_03_subs:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'leaf', 1)"
                    cursor.execute(sql, (code, dim_map['LAYOUT'], name, weight, max_score, criteria, order, layout_03_id))

                conn.commit()
                print("✓ 优化生产力布局指标完成 (4个)")

                # ============== 政策执行能力指标 (8个叶子指标) ==============
                print("\n插入政策执行能力指标...")

                exec_parent = [
                    ('EXEC_01', '资金效能情况', 40.00, 4.00, 1),
                    ('EXEC_02', '基金管理人专业水平', 60.00, 6.00, 2),
                ]
                for code, name, weight, max_score, order in exec_parent:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, 'parent', 0)"
                    cursor.execute(sql, (code, dim_map['EXECUTION'], name, weight, max_score, f'{name}评分标准', order))

                conn.commit()

                cursor.execute("SELECT id FROM scoring_indicators WHERE indicator_code = 'EXEC_01'")
                exec_01_id = cursor.fetchone()['id']
                cursor.execute("SELECT id FROM scoring_indicators WHERE indicator_code = 'EXEC_02'")
                exec_02_id = cursor.fetchone()['id']

                # EXEC_01 子指标 (4个)
                print("  插入EXEC_01子指标...")
                exec_01_subs = [
                    ('EXEC_01_01', '出资完成比例', 25.0, 1.0, 11, '≥50%%=1分，30%%-50%%=0.5分，<30%%=0分'),
                    ('EXEC_01_02', '闲置资金情况', 25.0, 1.0, 12, '闲置资金占比<30%%=1分，闲置资金占比≥30%%=0分'),
                    ('EXEC_01_03', '内部收益率', 25.0, 1.0, 13, '内部收益率≥3%%=1分，内部收益率<3%%=0分'),
                    ('EXEC_01_04', '资产增值率', 25.0, 1.0, 14, '资产增值率≥5%%=1分，资产增值率<5%%=0分'),
                ]
                for code, name, weight, max_score, order, criteria in exec_01_subs:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'leaf', 1)"
                    cursor.execute(sql, (code, dim_map['EXECUTION'], name, weight, max_score, criteria, order, exec_01_id))

                # EXEC_02 子指标 (4个)
                print("  插入EXEC_02子指标...")
                exec_02_subs = [
                    ('EXEC_02_01', '高级管理人员从业年限', 16.67, 1.0, 21, '从业年限>10年=1分，从业年限≤10年=0分'),
                    ('EXEC_02_02', '风险防控有效性', 16.67, 1.0, 22, '有制度且无风险损失=1分，无制度或发生风险损失/爆雷=0分'),
                    ('EXEC_02_03', '信用建设情况', 33.33, 2.0, 23, '信用情况较好=2分，信用情况较差=0分'),
                    ('EXEC_02_04', '信息报送及披露', 33.33, 2.0, 24, '信息登记较好且披露透明度高=2分，信息登记较好或披露透明度高=1分，信息登记较差且披露透明度不足=0分'),
                ]
                for code, name, weight, max_score, order, criteria in exec_02_subs:
                    sql = "INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'leaf', 1)"
                    cursor.execute(sql, (code, dim_map['EXECUTION'], name, weight, max_score, criteria, order, exec_02_id))

                conn.commit()
                print("✓ 政策执行能力指标完成 (8个)")

                # 验证结果
                print("\n验证结果:")
                cursor.execute("SELECT COUNT(*) as count FROM scoring_dimensions WHERE is_active = TRUE")
                dim_count = cursor.fetchone()['count']
                print(f"✓ 维度数量: {dim_count}")

                cursor.execute("SELECT COUNT(*) as count FROM scoring_indicators WHERE is_active = TRUE")
                ind_count = cursor.fetchone()['count']
                print(f"✓ 指标总数: {ind_count}")

                cursor.execute("SELECT COUNT(*) as count FROM scoring_indicators WHERE indicator_type = 'leaf' AND is_active = TRUE")
                leaf_count = cursor.fetchone()['count']
                print(f"✓ 叶子指标（实际评分项）: {leaf_count}")

                cursor.execute("""
                    SELECT sd.dimension_code, COUNT(*) as count
                    FROM scoring_indicators si
                    JOIN scoring_dimensions sd ON si.dimension_id = sd.id
                    WHERE si.indicator_type = 'leaf' AND si.is_active = TRUE AND sd.is_active = TRUE
                    GROUP BY sd.dimension_code
                    ORDER BY sd.dimension_code
                """)
                print("\n按维度统计叶子指标:")
                for row in cursor.fetchall():
                    print(f"  {row['dimension_code']}: {row['count']}个")

                print("\n✅ 评分数据初始化完成！")
                print(f"\n现在您可以开始评分了。总共有 {leaf_count} 个叶子指标需要评分。")
                return True

    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    init_scoring_data()
