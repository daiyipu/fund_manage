-- 政府投资基金投向评分系统 - 数据库表结构
-- 创建数据库: CREATE DATABASE fund_scoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'manager', 'scorer', 'viewer') NOT NULL DEFAULT 'viewer',
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_department (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 项目表
CREATE TABLE IF NOT EXISTS projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_code VARCHAR(50) UNIQUE NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    fund_name VARCHAR(200),
    fund_manager VARCHAR(200),
    investment_amount DECIMAL(15,2),
    investment_date DATE,
    region VARCHAR(100),
    industry VARCHAR(100),
    project_stage ENUM('seed', 'early', 'growth', 'mature') DEFAULT 'early',
    description TEXT,
    status ENUM('draft', 'submitted', 'scoring', 'completed', 'archived') DEFAULT 'draft',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_region (region),
    INDEX idx_industry (industry),
    INDEX idx_project_stage (project_stage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 评分维度表
CREATE TABLE IF NOT EXISTS scoring_dimensions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dimension_code VARCHAR(50) UNIQUE NOT NULL,
    dimension_name VARCHAR(200) NOT NULL,
    weight DECIMAL(5,2) NOT NULL COMMENT '权重百分比',
    max_score DECIMAL(5,2) NOT NULL COMMENT '最高分值',
    description TEXT,
    display_order INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 评分指标表
CREATE TABLE IF NOT EXISTS scoring_indicators (
    id INT PRIMARY KEY AUTO_INCREMENT,
    indicator_code VARCHAR(50) UNIQUE NOT NULL,
    dimension_id INT NOT NULL,
    indicator_name VARCHAR(200) NOT NULL,
    weight DECIMAL(5,2) NOT NULL COMMENT '权重百分比',
    max_score DECIMAL(5,2) NOT NULL COMMENT '最高分值',
    scoring_criteria TEXT COMMENT '评分标准说明',
    display_order INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dimension_id) REFERENCES scoring_dimensions(id) ON DELETE CASCADE,
    INDEX idx_dimension (dimension_id),
    INDEX idx_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 项目评分记录表
CREATE TABLE IF NOT EXISTS project_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    dimension_id INT NOT NULL,
    indicator_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL COMMENT '原始评分',
    weighted_score DECIMAL(5,2) NOT NULL COMMENT '加权后得分',
    scorer_id INT NOT NULL,
    scorer_comment TEXT,
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (dimension_id) REFERENCES scoring_dimensions(id),
    FOREIGN KEY (indicator_id) REFERENCES scoring_indicators(id),
    FOREIGN KEY (scorer_id) REFERENCES users(id),
    UNIQUE KEY uk_project_indicator (project_id, indicator_id),
    INDEX idx_project (project_id),
    INDEX idx_scorer (scorer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 评分汇总表
CREATE TABLE IF NOT EXISTS scoring_summaries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    dimension_id INT NOT NULL,
    total_score DECIMAL(5,2) NOT NULL COMMENT '维度总分',
    weighted_total DECIMAL(5,2) NOT NULL COMMENT '维度加权总分',
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (dimension_id) REFERENCES scoring_dimensions(id),
    UNIQUE KEY uk_project_dimension (project_id, dimension_id),
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 项目总分表
CREATE TABLE IF NOT EXISTS project_total_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    total_score DECIMAL(5,2) NOT NULL COMMENT '项目总分',
    policy_score DECIMAL(5,2) NOT NULL COMMENT '政策符合性得分',
    layout_score DECIMAL(5,2) NOT NULL COMMENT '优化生产力布局得分',
    execution_score DECIMAL(5,2) NOT NULL COMMENT '政策执行能力得分',
    rank_in_period INT,
    grade VARCHAR(50) COMMENT '评级：excellent/good/qualified/unqualified',
    reviewed_by INT,
    review_comment TEXT,
    reviewed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id),
    UNIQUE KEY uk_project (project_id),
    INDEX idx_grade (grade),
    INDEX idx_rank (rank_in_period)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. 审批记录表
CREATE TABLE IF NOT EXISTS approval_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    action ENUM('submit', 'approve', 'reject', 'return') NOT NULL,
    actor_id INT NOT NULL,
    actor_role VARCHAR(50) NOT NULL,
    comment TEXT,
    action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES users(id),
    INDEX idx_project (project_id),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. 附件表
CREATE TABLE IF NOT EXISTS attachments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    uploaded_by INT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. 系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
