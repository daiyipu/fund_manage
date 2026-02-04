"""
用户数据访问类
"""
from typing import List, Optional
import logging

from app.utils.database import get_db_connection, hash_password, verify_password

logger = logging.getLogger(__name__)


class UserRepository:
    """用户数据访问类"""

    def create(self, user: dict) -> int:
        """创建新用户"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查用户名是否已存在
                    cursor.execute("SELECT id FROM users WHERE username = %s", (user['username'],))
                    if cursor.fetchone():
                        raise ValueError(f"Username {user['username']} already exists")

                    # 密码加密
                    password_hash = hash_password(user['password'])

                    sql = """
                        INSERT INTO users (username, password_hash, real_name, email, role, department)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        user['username'], password_hash, user['real_name'],
                        user.get('email'), user.get('role', 'viewer'), user.get('department')
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    def get_by_id(self, user_id: int) -> Optional[dict]:
        """根据ID获取用户"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM users WHERE id = %s"
                    cursor.execute(sql, (user_id,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by id: {str(e)}")
            raise

    def get_by_username(self, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM users WHERE username = %s"
                    cursor.execute(sql, (username,))
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """验证用户登录"""
        try:
            user = self.get_by_username(username)
            if not user:
                return None

            if not user['is_active']:
                raise ValueError("User account is inactive")

            if verify_password(password, user['password_hash']):
                # 返回用户信息（不包含密码）
                user.pop('password_hash', None)
                return user

            return None
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise

    def update(self, user_id: int, user: dict) -> bool:
        """更新用户信息"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        UPDATE users SET
                            real_name = %s, email = %s, role = %s, department = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        user['real_name'], user.get('email'),
                        user.get('role'), user.get('department'),
                        user_id
                    ))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

    def change_password(self, user_id: int, new_password: str) -> bool:
        """修改用户密码"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    password_hash = hash_password(new_password)
                    sql = "UPDATE users SET password_hash = %s WHERE id = %s"
                    cursor.execute(sql, (password_hash, user_id))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise

    def deactivate(self, user_id: int) -> bool:
        """停用用户"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "UPDATE users SET is_active = FALSE WHERE id = %s"
                    cursor.execute(sql, (user_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            raise

    def activate(self, user_id: int) -> bool:
        """激活用户"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "UPDATE users SET is_active = TRUE WHERE id = %s"
                    cursor.execute(sql, (user_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error activating user: {str(e)}")
            raise

    def list_users(
        self,
        role: Optional[str] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[dict]:
        """查询用户列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM users WHERE 1=1"
                    params = []

                    if role:
                        sql += " AND role = %s"
                        params.append(role)
                    if department:
                        sql += " AND department = %s"
                        params.append(department)
                    if is_active is not None:
                        sql += " AND is_active = %s"
                        params.append(is_active)

                    sql += " ORDER BY created_at DESC LIMIT %s"
                    params.append(limit)

                    cursor.execute(sql, params)
                    users = cursor.fetchall()
                    # 不返回密码哈希
                    for user in users:
                        user.pop('password_hash', None)
                    return users
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise

    def get_departments(self) -> List[str]:
        """获取所有部门列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT DISTINCT department FROM users WHERE department IS NOT NULL ORDER BY department"
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    return [r['department'] for r in results]
        except Exception as e:
            logger.error(f"Error getting departments: {str(e)}")
            raise
