-- 基金投向评分系统 - 数据库迁移
-- 创建 funds 表（基金表）

-- 1. 创建基金表
CREATE TABLE IF NOT EXISTS funds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fund_code VARCHAR(50) UNIQUE NOT NULL COMMENT '基金编码',
    fund_name VARCHAR(200) NOT NULL COMMENT '基金名称',
    fund_manager VARCHAR(200) NOT NULL COMMENT '基金管理人',
    total_amount DECIMAL(15,2) COMMENT '基金总规模（万元）',
    establishment_date DATE COMMENT '成立日期',
    fund_type VARCHAR(50) COMMENT '基金类型（如：产业投资基金、创业投资基金等）',
    region VARCHAR(100) COMMENT '注册地区',
    department VARCHAR(100) COMMENT '主管部门',
    description TEXT COMMENT '基金描述',
    status ENUM('draft', 'active', 'completed', 'archived') DEFAULT 'draft',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_region (region),
    INDEX idx_fund_type (fund_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
