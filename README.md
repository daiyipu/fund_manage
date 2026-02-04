# 政府投资基金投向评分系统

基于《政府投资基金投向评价管理办法（试行）》开发的部门级协作评分系统，用于对政府投资基金投资项目进行多维度评分评价。

## 技术栈

- 后端：Python 3.10+
- 前端：Streamlit 1.31.0
- 数据库：MySQL 5.7+ / MariaDB 10.3+

## 核心功能

### 评分维度

根据管理办法，系统实现了三大评分维度，共13个具体指标：

#### 1. 政策符合性指标（60分）
- 支持新质生产力发展情况（10分）
- 支持科技创新和促进成果转化情况（10分）
- 推进全国统一大市场建设情况（10分）
- 支持绿色发展情况（5分）
- 支持民营经济发展和促进民间投资情况（5分）
- 壮大耐心资本情况（5分）
- 带动社会资本情况（5分）
- 服务社会民生等其他重点领域情况（10分）

#### 2. 优化生产力布局指标（30分）
- 落实国家区域战略情况（10分）
- 重点投向领域契合度（10分）
- 产能有效利用情况（10分）

#### 3. 政策执行能力指标（10分）
- 资金效能情况（4分）
- 基金管理人专业水平（6分）

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE fund_scoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 初始化数据表

```bash
# 导入表结构
mysql -u root -p fund_scoring < database/schema.sql

# 导入初始数据（评分维度和指标）
mysql -u root -p fund_scoring < database/seeds/scoring_data.sql
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，设置数据库连接信息
```

**.env配置示例**：
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fund_scoring
DB_USER=root
DB_PASSWORD=your_mysql_password
```

### 5. 创建管理员用户

```bash
python -c "
from app.utils.database import create_admin_user
create_admin_user(
    username='admin',
    password='admin123',
    real_name='系统管理员',
    role='admin',
    department='信息技术部'
)
"
```

### 6. 启动应用

```bash
# 方式1：使用启动脚本
python run.py

# 方式2：直接使用streamlit
streamlit run app/main.py

# 访问应用
# 浏览器打开 http://localhost:8501
```

### 7. 登录系统

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

## 项目结构

```
fund_manage/
├── app/                      # Streamlit应用
│   ├── main.py              # 应用入口
│   ├── utils/               # 工具函数
│   │   ├── database.py      # 数据库连接
│   │   └── scoring.py       # 评分计算逻辑
│   └── ...
├── core/                     # 核心业务逻辑
│   ├── models.py            # 数据模型
│   ├── services/            # 业务服务层
│   │   ├── scoring_service.py
│   │   ├── project_service.py
│   │   └── user_service.py
│   └── repositories/        # 数据访问层
│       ├── scoring_repository.py
│       ├── project_repository.py
│       └── user_repository.py
├── config/                   # 配置文件
│   ├── settings.py          # 应用配置
│   └── scoring_rules.py     # 评分规则配置
├── database/                 # 数据库相关
│   ├── schema.sql           # 建表脚本
│   └── seeds/               # 初始数据
├── requirements.txt          # Python依赖
├── .env.example             # 环境变量模板
└── run.py                   # 启动脚本
```

## 用户角色

系统支持四种角色，权限各不相同：

1. **admin（系统管理员）**
   - 所有权限
   - 用户管理

2. **manager（部门负责人）**
   - 创建项目、分配评分任务
   - 审批评分结果
   - 查看所有项目和统计数据

3. **scorer（评分专家）**
   - 对分配的项目进行评分
   - 查看自己的评分记录

4. **viewer（查看人员）**
   - 查看项目和评分结果
   - 导出报告

## 评分流程

1. **创建项目**：管理员或部门负责人创建待评分项目
2. **录入评分**：评分专家选择项目，按三大维度13个指标录入评分
3. **自动计算**：系统自动计算：
   - 指标加权得分
   - 维度加权总分
   - 项目总分
   - 等级评定（优秀/良好/合格/不合格）
   - 项目排名
4. **查看结果**：查看评分详情、导出报告

## 等级评定标准

| 总分范围 | 等级 |
|---------|------|
| ≥90分 | 优秀 |
| ≥80分 | 良好 |
| ≥60分 | 合格 |
| <60分 | 不合格 |

## 生产环境部署

### 使用systemd管理服务

创建服务文件 `/etc/systemd/system/fund-scoring.service`：

```ini
[Unit]
Description=Government Investment Fund Scoring System
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/fund_manage
Environment="PATH=/path/to/fund_manage/venv/bin"
ExecStart=/path/to/fund_manage/venv/bin/streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable fund-scoring
sudo systemctl start fund-scoring
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 数据备份

创建定时备份脚本：
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u root -p fund_scoring > $BACKUP_DIR/fund_scoring_$DATE.sql
find $BACKUP_DIR -name "fund_scoring_*.sql" -mtime +30 -delete
```

添加到crontab：
```bash
0 2 * * * /path/to/backup.sh
```

## 开发说明

### 添加新的评分指标

1. 编辑 `config/scoring_rules.py`，在 `SCORING_DIMENSIONS` 中添加新指标
2. 执行SQL插入新的指标记录到 `scoring_indicators` 表
3. 重启应用

### 修改评分规则

编辑 `config/scoring_rules.py` 文件：
- 修改权重和最高分
- 调整评分标准
- 修改等级划分标准

## 常见问题

**Q: 数据库连接失败？**
A: 检查.env文件中的数据库配置，确保MySQL服务已启动

**Q: 评分结果不对？**
A: 检查scoring_rules.py中的权重设置是否正确，确保所有指标都已评分

**Q: 如何重置管理员密码？**
A: 使用user_service的change_password方法或直接修改数据库

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请联系开发团队。
