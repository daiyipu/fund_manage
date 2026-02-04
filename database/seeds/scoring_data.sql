-- 初始化评分维度和指标数据
-- 使用方法: mysql -u root -p fund_scoring < database/seeds/scoring_data.sql

-- 清空现有数据（可选，用于重新初始化）
-- DELETE FROM scoring_indicators;
-- DELETE FROM scoring_dimensions;

-- 插入评分维度
INSERT INTO scoring_dimensions (dimension_code, dimension_name, weight, max_score, description, display_order) VALUES
('POLICY', '政策符合性指标', 60.00, 60.00, '评价项目与国家政策导向的符合程度', 1),
('LAYOUT', '优化生产力布局指标', 30.00, 30.00, '评价项目对优化生产力布局的贡献', 2),
('EXECUTION', '政策执行能力指标', 10.00, 10.00, '评价基金管理人的政策执行能力', 3);

-- 插入政策符合性指标（8个指标，共60分）
-- 注意：需要先获取维度ID，这里假设插入后的ID为1,2,3
-- 如果ID不同，需要手动调整下面的dimension_id值

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order) VALUES
-- 政策符合性指标 (dimension_id = 1)
('POLICY_01', 1, '支持新质生产力发展情况', 16.67, 10.00, '评价项目在发展新质生产力方面的贡献程度', 1),
('POLICY_02', 1, '支持科技创新和促进成果转化情况', 16.67, 10.00, '评价项目在科技创新和成果转化方面的表现', 2),
('POLICY_03', 1, '推进全国统一大市场建设情况', 16.67, 10.00, '评价项目对统一大市场建设的促进作用', 3),
('POLICY_04', 1, '支持绿色发展情况', 8.33, 5.00, '评价项目在绿色发展和环保方面的贡献', 4),
('POLICY_05', 1, '支持民营经济发展和促进民间投资情况', 8.33, 5.00, '评价项目对民营经济发展的支持程度', 5),
('POLICY_06', 1, '壮大耐心资本情况', 8.33, 5.00, '评价项目对培育长期资本的作用', 6),
('POLICY_07', 1, '带动社会资本情况', 8.33, 5.00, '评价项目撬动社会资本的能力', 7),
('POLICY_08', 1, '服务社会民生等其他重点领域情况', 16.67, 10.00, '评价项目在民生等重点领域的贡献', 8);

-- 插入优化生产力布局指标（3个指标，共30分）
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order) VALUES
-- 优化生产力布局指标 (dimension_id = 2)
('LAYOUT_01', 2, '落实国家区域战略情况', 33.33, 10.00, '评价项目对国家区域战略的落实程度', 1),
('LAYOUT_02', 2, '重点投向领域契合度', 33.33, 10.00, '评价项目投向与重点领域的契合程度', 2),
('LAYOUT_03', 2, '产能有效利用情况', 33.33, 10.00, '评价项目对产能有效利用的促进情况', 3);

-- 插入政策执行能力指标（2个指标，共10分）
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order) VALUES
-- 政策执行能力指标 (dimension_id = 3)
('EXEC_01', 3, '资金效能情况', 40.00, 4.00, '评价资金使用的效率和效益', 1),
('EXEC_02', 3, '基金管理人专业水平', 60.00, 6.00, '评价基金管理人的专业能力和经验', 2);

-- 查询验证
-- SELECT * FROM scoring_dimensions ORDER BY display_order;
-- SELECT si.*, sd.dimension_name FROM scoring_indicators si JOIN scoring_dimensions sd ON si.dimension_id = sd.id ORDER BY sd.display_order, si.display_order;
