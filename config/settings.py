"""
应用配置模块
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '3306'))
    database: str = os.getenv('DB_NAME', 'fund_scoring')
    user: str = os.getenv('DB_USER', 'root')
    password: str = os.getenv('DB_PASSWORD', '')
    charset: str = 'utf8mb4'


@dataclass
class AppConfig:
    """应用配置"""
    app_name: str = '政府投资基金投向评分系统'
    version: str = '1.0.0'
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    secret_key: str = os.getenv('SECRET_KEY', 'your-secret-key-here')
    max_upload_size: int = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB
    allowed_extensions: set = None
    session_timeout: int = int(os.getenv('SESSION_TIMEOUT', '7200'))  # 2小时

    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}


@dataclass
class ScoringConfig:
    """评分配置"""
    # 等级划分标准
    grade_excellent_min: float = 90.0  # 优秀
    grade_good_min: float = 80.0  # 良好
    grade_qualified_min: float = 60.0  # 合格
    # 低于60分为不合格


# 全局配置实例
db_config = DatabaseConfig()
app_config = AppConfig()
scoring_config = ScoringConfig()
