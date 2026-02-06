-- 基金投向评分系统 - 数据库迁移
-- 创建 investments 表（投资表）- 替代 projects

-- 1. 创建投资表
CREATE TABLE IF NOT EXISTS investments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fund_id INT NOT NULL COMMENT '所属基金ID',
    investment_code VARCHAR(50) UNIQUE NOT NULL COMMENT '投资编码',
    investment_name VARCHAR(200) NOT NULL COMMENT '投资名称/投向项目名称',
    investment_amount DECIMAL(15,2) COMMENT '本次投资金额（万元）',
    investment_date DATE COMMENT '投资日期',
    industry VARCHAR(100) COMMENT '投向行业',
    investment_stage ENUM('seed', 'early', 'growth', 'mature') DEFAULT 'early' COMMENT '投资阶段',
    description TEXT COMMENT '投资描述',
    status ENUM('draft', 'submitted', 'scoring', 'completed', 'archived') DEFAULT 'draft',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES funds(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_fund_id (fund_id),
    INDEX idx_status (status),
    INDEX idx_industry (industry),
    INDEX idx_investment_stage (investment_stage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
