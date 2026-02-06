-- 基金投向评分系统 - 数据库迁移
-- 将 project_scores 重命名为 investment_scores

-- 步骤1: 重命名表
RENAME TABLE project_scores TO investment_scores;

-- 步骤2: 修改字段名 project_id -> investment_id
ALTER TABLE investment_scores
CHANGE COLUMN project_id investment_id INT NOT NULL COMMENT '投资ID';

-- 步骤3: 添加外键约束
-- 首先删除可能存在的旧外键
ALTER TABLE investment_scores DROP FOREIGN KEY IF EXISTS project_scores_ibfk_1;

-- 添加新的外键约束
ALTER TABLE investment_scores
ADD CONSTRAINT fk_investment_scores_investment
FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE;
