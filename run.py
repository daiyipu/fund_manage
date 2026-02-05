"""
政府投资基金投向评分系统 - 启动脚本
"""
import sys
import subprocess
from pathlib import Path


def main():
    """启动Streamlit应用"""
    # 确保在正确的目录
    project_root = Path(__file__).parent
    app_main = project_root / "app" / "main.py"

    if not app_main.exists():
        print(f"错误: 找不到应用入口文件 {app_main}")
        sys.exit(1)

    # 启动Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_main),
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--logger.level", "info"
    ]

    print(f"正在启动 {app_main}...")
    print(f"访问地址: http://localhost:8501")
    print("按 Ctrl+C 停止服务")

    try:
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n服务已停止")


if __name__ == "__main__":
    main()
