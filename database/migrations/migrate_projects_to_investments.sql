-- 基金投向评分系统 - 数据迁移脚本
-- 将现有的 projects 数据迁移到新的 funds + investments 结构

-- 步骤1: 为现有的 project 创建对应的基金
-- 如果 project 有 fund_name，则创建或关联基金；否则创建一个默认基金

INSERT INTO funds (fund_code, fund_name, fund_manager, region, department, status, created_by)
SELECT
    CONCAT('FUND_', p.project_code) as fund_code,
    COALESCE(p.fund_name, CONCAT(p.project_name, '-基金')) as fund_name,
    COALESCE(p.fund_manager, '待定') as fund_manager,
    p.region,
    '默认部门' as department,
    'active' as status,
    p.created_by
FROM projects p
WHERE NOT EXISTS (
    SELECT 1 FROM funds f WHERE f.fund_code = CONCAT('FUND_', p.project_code)
);

-- 步骤2: 将 projects 数据迁移到 investments
INSERT INTO investments (
    fund_id,
    investment_code,
    investment_name,
    investment_amount,
    investment_date,
    industry,
    investment_stage,
    description,
    status,
    created_by,
    created_at,
    updated_at
)
SELECT
    (SELECT id FROM funds WHERE fund_code = CONCAT('FUND_', p.project_code)) as fund_id,
    p.project_code as investment_code,
    p.project_name as investment_name,
    p.investment_amount,
    p.investment_date,
    p.industry,
    p.project_stage as investment_stage,
    p.description,
    p.status,
    p.created_by,
    p.created_at,
    p.updated_at
FROM projects p
WHERE NOT EXISTS (
    SELECT 1 FROM investments i WHERE i.investment_code = p.project_code
);

-- 步骤3: 验证迁移结果
-- SELECT 'Funds created:' as info, COUNT(*) as count FROM funds;
-- SELECT 'Investments created:' as info, COUNT(*) as count FROM investments;
-- SELECT 'Original projects:' as info, COUNT(*) as count FROM projects;
