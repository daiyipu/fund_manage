"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.database import init_database, create_admin_user, test_connection


def main():
    """初始化数据库"""
    print("=" * 50)
    print("政府投资基金投向评分系统 - 数据库初始化")
    print("=" * 50)
    print()

    # 1. 创建数据库
    print("步骤 1/3: 创建数据库...")
    if init_database():
        print("✓ 数据库创建成功")
    else:
        print("✗ 数据库创建失败")
        return

    print()

    # 2. 导入表结构
    print("步骤 2/3: 导入表结构...")
    try:
        import pymysql
        from app.utils.database import get_db_connection

        # 读取schema.sql文件
        schema_file = Path(__file__).parent / "database" / "schema.sql"
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 执行SQL（按语句分割）
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 分割SQL语句
                statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

                for statement in statements:
                    if statement:
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            # 忽略已存在的表错误
                            if "already exists" not in str(e):
                                print(f"  警告: {str(e)}")

                conn.commit()
        print("✓ 表结构导入成功")
    except Exception as e:
        print(f"✗ 表结构导入失败: {str(e)}")
        return

    print()

    # 3. 导入初始数据
    print("步骤 3/3: 导入初始数据（评分维度和指标）...")
    try:
        # 读取scoring_data.sql文件
        data_file = Path(__file__).parent / "database" / "seeds" / "scoring_data.sql"
        with open(data_file, 'r', encoding='utf-8') as f:
            data_sql = f.read()

        # 执行SQL
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 分割SQL语句
                statements = [s.strip() for s in data_sql.split(';') if s.strip()]

                for statement in statements:
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            if "Duplicate entry" not in str(e):
                                print(f"  警告: {str(e)}")

                conn.commit()
        print("✓ 初始数据导入成功")
    except Exception as e:
        print(f"✗ 初始数据导入失败: {str(e)}")
        return

    print()
    print("=" * 50)
    print("测试数据库连接...")
    if test_connection():
        print("✓ 数据库连接测试成功")
    else:
        print("✗ 数据库连接测试失败")

    print()
    print("=" * 50)
    print("创建管理员用户...")
    print()

    try:
        # 获取管理员账号信息
        import os
        from dotenv import load_dotenv
        load_dotenv()

        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')

        if create_admin_user(
            username=admin_username,
            password=admin_password,
            real_name='系统管理员',
            role='admin',
            department='信息技术部',
            email=admin_email
        ):
            print(f"✓ 管理员用户创建成功")
            print(f"  用户名: {admin_username}")
            print(f"  密码: {admin_password}")
        else:
            print("✗ 管理员用户创建失败（可能已存在）")
    except Exception as e:
        print(f"✗ 管理员用户创建失败: {str(e)}")

    print()
    print("=" * 50)
    print("✓ 数据库初始化完成！")
    print()
    print("您现在可以运行以下命令启动应用：")
    print("  python run.py")
    print()
    print("或使用streamlit直接启动：")
    print("  streamlit run app/main.py")
    print()
    print("访问地址: http://localhost:8501")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误: {str(e)}")
        print("\n请检查:")
        print("1. .env 文件中的数据库配置是否正确")
        print("2. MySQL服务是否已启动")
        print("3. 数据库用户是否有创建数据库的权限")
        sys.exit(1)
