"""
验证scoring_rules.py配置完整性

根据《政府投资基金投向评价管理办法（试行）》验证所有13个指标的scoring_guide配置
"""
from config.scoring_rules import SCORING_DIMENSIONS
from decimal import Decimal

def verify_scoring_guide_completeness():
    """验证每个指标的scoring_guide是否覆盖完整 - 支持层级指标"""
    errors = []
    warnings = []

    for dim_code, dimension in SCORING_DIMENSIONS.items():
        print(f"\n=== 验证维度: {dimension['name']} ({dim_code}) ===")

        for indicator in dimension['indicators']:
            indicator_name = f"{indicator['code']}: {indicator['name']}"
            indicator_type = indicator.get('type', 'leaf')  # 默认为leaf

            # 处理父指标（包含子指标）
            if indicator_type == 'parent':
                sub_indicators = indicator.get('sub_indicators', [])

                if not sub_indicators:
                    errors.append(f"{indicator_name}: 父指标缺少sub_indicators配置")
                    continue

                # 验证所有子指标
                for sub in sub_indicators:
                    sub_name = f"{sub['code']}: {sub['name']}"
                    guide = sub.get('scoring_guide', {})
                    max_score = Decimal(str(sub['max_score']))

                    if not guide:
                        errors.append(f"{sub_name}: 子指标缺少scoring_guide配置")
                        continue

                    # 检查是否有0分档位
                    has_zero = '0' in guide or '0.0' in guide
                    if not has_zero:
                        errors.append(f"{sub_name}: 缺少0分档位")

                    # 检查是否有满分档位
                    max_score_str = str(max_score) if max_score == int(max_score) else f"{max_score:.2f}"
                    max_score_str = max_score_str.rstrip('0').rstrip('.')
                    has_max = any(key == max_score_str or Decimal(key) == max_score for key in guide.keys())
                    if not has_max:
                        errors.append(f"{sub_name}: 缺少{max_score}分档位")

                    # 显示配置信息
                    print(f"\n  ├─ {sub_name}")
                    print(f"  │   满分: {max_score}分")
                    print(f"  │   档位数: {len(guide)}个")
                    print(f"  │   范围: {min(guide.keys())}分 - {max(guide.keys())}分")
                    print(f"  │   示例选项: {list(guide.values())[0]}")

                print(f"\n✓ {indicator_name} (父指标，含{len(sub_indicators)}个子指标)")

            # 处理叶子指标（直接评分）
            else:
                guide = indicator.get('scoring_guide', {})
                max_score = Decimal(str(indicator['max_score']))

                # 检查是否有scoring_guide
                if not guide:
                    errors.append(f"{indicator_name}: 缺少scoring_guide配置")
                    continue

                # 检查是否有0分档位
                has_zero = '0' in guide or '0.0' in guide
                if not has_zero:
                    errors.append(f"{indicator_name}: 缺少0分档位")

                # 检查是否有满分档位
                max_score_str = str(max_score) if max_score == int(max_score) else f"{max_score:.2f}"
                max_score_str = max_score_str.rstrip('0').rstrip('.')
                has_max = any(key == max_score_str or Decimal(key) == max_score for key in guide.keys())
                if not has_max:
                    errors.append(f"{indicator_name}: 缺少{max_score}分档位")

                # 检查分数是否按降序排列
                try:
                    scores = [Decimal(score) for score in guide.keys()]
                    if sorted(scores, reverse=True) != scores:
                        warnings.append(f"{indicator_name}: 分数档位未按降序排列（建议但不影响功能）")
                except Exception as e:
                    errors.append(f"{indicator_name}: 分数解析失败 - {str(e)}")

                # 显示配置信息
                print(f"\n✓ {indicator_name}")
                print(f"  满分: {max_score}分")
                print(f"  档位数: {len(guide)}个")
                print(f"  范围: {min(guide.keys())}分 - {max(guide.keys())}分")
                print(f"  示例选项: {list(guide.values())[0]}")

    return errors, warnings

def verify_all_indicators():
    """验证是否包含所有13个指标"""
    expected_indicators = {
        'POLICY': ['POLICY_01', 'POLICY_02', 'POLICY_03', 'POLICY_04', 'POLICY_05', 'POLICY_06', 'POLICY_07', 'POLICY_08'],
        'LAYOUT': ['LAYOUT_01', 'LAYOUT_02', 'LAYOUT_03'],
        'EXECUTION': ['EXEC_01', 'EXEC_02']
    }

    missing = []
    for dim_code, expected_codes in expected_indicators.items():
        dimension = SCORING_DIMENSIONS.get(dim_code)
        if not dimension:
            missing.append(f"{dim_code}: 维度不存在")
            continue

        actual_codes = [ind['code'] for ind in dimension['indicators']]
        for code in expected_codes:
            if code not in actual_codes:
                missing.append(f"{dim_code}: 缺少指标{code}")

    return missing

if __name__ == '__main__':
    print("=" * 70)
    print("政府投资基金投向评分系统 - 配置完整性验证")
    print("=" * 70)

    # 验证所有13个指标是否存在
    print("\n### 第一步: 验证指标完整性 ###")
    missing = verify_all_indicators()
    if missing:
        print("\n❌ 发现缺失的指标：")
        for m in missing:
            print(f"  - {m}")
    else:
        print("\n✓ 所有13个指标配置完整")

    # 验证scoring_guide配置
    print("\n### 第二步: 验证scoring_guide配置 ###")
    errors, warnings = verify_scoring_guide_completeness()

    # 输出结果
    print("\n" + "=" * 70)
    print("### 验证结果 ###")
    print("=" * 70)

    if errors:
        print("\n❌ 发现配置错误：")
        for error in errors:
            print(f"  - {error}")
        print("\n请修复上述错误后再使用系统。")
    elif warnings:
        print("\n⚠️ 发现配置警告（不影响功能）：")
        for warning in warnings:
            print(f"  - {warning}")
        print("\n配置验证通过！建议优化警告项。")
    else:
        print("\n✅ 配置验证通过！所有13个指标的scoring_guide配置完整且正确。")

    # 统计信息
    total_indicators = sum(len(d['indicators']) for d in SCORING_DIMENSIONS.values())
    total_guides = sum(sum(1 for ind in d['indicators'] if ind.get('scoring_guide')) for d in SCORING_DIMENSIONS.values())
    avg_options = sum(len(ind.get('scoring_guide', {})) for d in SCORING_DIMENSIONS.values() for ind in d['indicators']) / total_indicators

    print(f"\n### 统计信息 ###")
    print(f"  总维度数: {len(SCORING_DIMENSIONS)}")
    print(f"  总指标数: {total_indicators}")
    print(f"  已配置scoring_guide的指标: {total_guides}")
    print(f"  平均每个指标的选项数: {avg_options:.1f}")
    print("=" * 70)
