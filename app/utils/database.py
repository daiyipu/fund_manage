"""
数据库连接管理
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import logging

from config.settings import db_config

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    获取数据库连接的上下文管理器

    使用示例:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                result = cursor.fetchall()
    """
    connection = None
    try:
        connection = pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            password=db_config.password,
            database=db_config.database,
            charset=db_config.charset,
            cursorclass=DictCursor
        )
        yield connection
    except pymysql.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if connection:
            connection.close()


def get_connection():
    """
    获取数据库连接（非上下文管理器版本）

    注意：使用此方法需要手动关闭连接
    """
    try:
        connection = pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            password=db_config.password,
            database=db_config.database,
            charset=db_config.charset,
            cursorclass=DictCursor
        )
        return connection
    except pymysql.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise


def test_connection():
    """测试数据库连接"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
                return result is not None
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False


def init_database():
    """
    初始化数据库
    创建数据库（如果不存在）
    """
    try:
        # 先连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            password=db_config.password,
            charset=db_config.charset
        )

        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.commit()
            logger.info(f"Database {db_config.database} initialized successfully")

        connection.close()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密

    Args:
        password: 明文密码

    Returns:
        哈希后的密码
    """
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码

    Args:
        password: 明文密码
        password_hash: 哈希后的密码

    Returns:
        是否匹配
    """
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_admin_user(
    username: str,
    password: str,
    real_name: str,
    role: str = 'admin',
    department: str = '信息技术部',
    email: str = None
):
    """
    创建初始管理员用户

    Args:
        username: 用户名
        password: 密码
        real_name: 真实姓名
        role: 角色
        department: 部门
        email: 邮箱
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 检查用户是否已存在
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    logger.warning(f"User {username} already exists")
                    return False

                # 创建用户
                password_hash = hash_password(password)
                sql = """
                    INSERT INTO users (username, password_hash, real_name, email, role, department)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (username, password_hash, real_name, email, role, department))
                conn.commit()
                logger.info(f"Admin user {username} created successfully")
                return True
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        return False
