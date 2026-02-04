-- Migration 002: Add Hierarchical Indicator Support
-- 添加层级指标支持
-- Date: 2025-02-04
-- Description: 为scoring_indicators表添加父子关系字段，支持子指标拆分

-- ===== Step 1: 添加层级关系字段 =====

ALTER TABLE scoring_indicators
ADD COLUMN parent_indicator_id INT NULL COMMENT '父指标ID，NULL表示顶级指标',
ADD COLUMN indicator_type ENUM('parent', 'leaf') DEFAULT 'leaf' COMMENT '指标类型：parent=父指标(仅汇总), leaf=叶子指标(实际评分)',
ADD COLUMN hierarchy_level INT DEFAULT 0 COMMENT '层级深度：0=顶级, 1=一级子指标, 2=二级子指标';

-- ===== Step 2: 添加外键约束和索引 =====

ALTER TABLE scoring_indicators
ADD FOREIGN KEY (parent_indicator_id) REFERENCES scoring_indicators(id) ON DELETE SET NULL,
ADD INDEX idx_parent (parent_indicator_id),
ADD INDEX idx_type (indicator_type),
ADD INDEX idx_hierarchy (hierarchy_level);

-- ===== Step 3: 将现有复合指标标记为父指标 =====

-- 更新需要拆分的指标为父指标
UPDATE scoring_indicators
SET indicator_type = 'parent', hierarchy_level = 0
WHERE indicator_code IN (
    'POLICY_02',   -- 支持科技创新和促进成果转化情况 → 3个子指标
    'POLICY_03',   -- 推进全国统一大市场建设情况 → 3个子指标
    'POLICY_04',   -- 支持绿色发展情况 → 2个子指标
    'POLICY_08',   -- 服务社会民生等其他重点领域情况 → 2个子指标
    'LAYOUT_03',   -- 产能有效利用情况 → 2个子指标
    'EXEC_01',     -- 资金效能情况 → 4个子指标
    'EXEC_02'      -- 基金管理人专业水平 → 4个子指标
);

-- ===== Step 4: 插入子指标记录 =====

-- POLICY_02 子指标 (3个)
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_02_01', dimension_id, '新增发明专利或技术成果', 30.0, 3.0, '新增6项及以上=3分，新增5项=2.5分，新增4项=2分，新增3项=1.5分，新增2项=1分，新增1项=0.5分，无新增=0分', display_order + 1, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_02';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_02_02', dimension_id, '支持科技成果转化', 20.0, 2.0, '支持科技成果转化=2分，无科技成果转化=0分', display_order + 2, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_02';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_02_03', dimension_id, '支持解决"卡脖子"难题', 50.0, 5.0, '支持多个"卡脖子"领域=5分，支持一个"卡脖子"领域=3分，不涉及"卡脖子"技术=0分', display_order + 3, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_02';

-- POLICY_03 子指标 (3个)
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_03_01', dimension_id, '返投比例情况', 30.0, 3.0, '未设置返投要求或<50%=3分，50%-100%=2分，100%-150%=1分，≥150%=0分', display_order + 1, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_03';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_03_02', dimension_id, '注册地迁移条件', 30.0, 3.0, '未设置注册地迁移条件=3分，设置了注册地迁移条件=0分', display_order + 2, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_03';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_03_03', dimension_id, '违规行为情况', 40.0, 4.0, '不存在违规行为=4分，存在违规行为=0分', display_order + 3, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_03';

-- POLICY_04 子指标 (2个)
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_04_01', dimension_id, '碳减排比例', 60.0, 3.0, '≥5%=3分，3%-5%=2分，1%-3%=1分，<1%或负数=0分', display_order + 1, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_04';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_04_02', dimension_id, '绿色发展投向比例', 40.0, 2.0, '投向比例>20%=2分，投向比例≤20%=1分，不涉及绿色发展领域=0分', display_order + 2, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_04';

-- POLICY_08 子指标 (2个)
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_08_01', dimension_id, '就业/税收/营收排名', 50.0, 5.0, '前10%=5分，前10%-30%=4分，30%-50%=3分，50%-70%=2分，70%-90%=1分，90%以后=0分', display_order + 1, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_08';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'POLICY_08_02', dimension_id, '重点领域贡献情况', 50.0, 5.0, '涉及两个及以上重点领域=5分，涉及一个重点领域=3分，不涉及重点领域=0分', display_order + 2, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'POLICY_08';

-- LAYOUT_03 子指标 (2个)
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'LAYOUT_03_01', dimension_id, '产能利用率', 50.0, 5.0, '高于行业平均水平=5分，接近平均水平±5%=3分，低于平均水平=0分', display_order + 1, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'LAYOUT_03';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'LAYOUT_03_02', dimension_id, '资产周转率', 50.0, 5.0, '≥100%=5分，80%-100%=4分，60%-80%=3分，<60%=0分', display_order + 2, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'LAYOUT_03';

-- EXEC_01 子指标 (4个)
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_01_01', dimension_id, '出资完成比例', 25.0, 1.0, '≥50%=1分，30%-50%=0.5分，<30%=0分', display_order + 1, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_01';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_01_02', dimension_id, '闲置资金情况', 25.0, 1.0, '闲置资金占比<30%=1分，闲置资金占比≥30%=0分', display_order + 2, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_01';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_01_03', dimension_id, '内部收益率', 25.0, 1.0, '内部收益率≥3%=1分，内部收益率<3%=0分', display_order + 3, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_01';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_01_04', dimension_id, '资产增值率', 25.0, 1.0, '资产增值率≥5%=1分，资产增值率<5%=0分', display_order + 4, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_01';

-- EXEC_02 子指标 (4个)
INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_02_01', dimension_id, '高级管理人员从业年限', 16.67, 1.0, '从业年限>10年=1分，从业年限≤10年=0分', display_order + 1, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_02';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_02_02', dimension_id, '风险防控有效性', 16.67, 1.0, '有制度且无风险损失=1分，无制度或发生风险损失/爆雷=0分', display_order + 2, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_02';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_02_03', dimension_id, '信用建设情况', 33.33, 2.0, '信用情况较好=2分，信用情况较差=0分', display_order + 3, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_02';

INSERT INTO scoring_indicators (indicator_code, dimension_id, indicator_name, weight, max_score, scoring_criteria, display_order, parent_indicator_id, indicator_type, hierarchy_level)
SELECT 'EXEC_02_04', dimension_id, '信息报送及披露', 33.33, 2.0, '信息登记较好且披露透明度高=2分，信息登记较好或披露透明度高=1分，信息登记较差且披露透明度不足=0分', display_order + 4, id, 'leaf', 1
FROM scoring_indicators WHERE indicator_code = 'EXEC_02';

-- ===== Step 5: 验证迁移结果 =====

-- 查看父指标数量
SELECT
    dimension_id,
    COUNT(*) as parent_count
FROM scoring_indicators
WHERE indicator_type = 'parent'
GROUP BY dimension_id;

-- 查看子指标数量
SELECT
    si.indicator_code as parent_code,
    si.indicator_name as parent_name,
    COUNT(child.id) as child_count
FROM scoring_indicators si
LEFT JOIN scoring_indicators child ON child.parent_indicator_id = si.id
WHERE si.indicator_type = 'parent'
GROUP BY si.id, si.indicator_code, si.indicator_name
ORDER BY si.indicator_code;

-- ===== 迁移完成 =====

-- 预期结果：
-- 7个父指标 (parent_indicator_id IS NULL, indicator_type = 'parent')
-- 18个子指标 (parent_indicator_id IS NOT NULL, indicator_type = 'leaf')
-- 总计: 13个原始指标 + 18个子指标 = 31个指标记录
