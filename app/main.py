"""
政府投资基金投向评分系统 - 主应用入口
"""
import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import app_config
from core.services.scoring_service import ScoringService
from core.services.project_service import ProjectService
from core.services.fund_service import fund_service
from core.services.investment_service import investment_service
from core.services.user_service import UserService

# 页面配置
st.set_page_config(
    page_title=app_config.app_name,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化服务
scoring_service = ScoringService()
project_service = ProjectService()  # 保留用于向后兼容
user_service = UserService()


# ============================================
# 增强的会话管理
# ============================================

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

# 创建logger用于会话管理
logger = logging.getLogger(__name__)

# 使用文件系统持久化会话存储
SESSION_STORE_FILE = Path(".streamlit/sessions.json")


def _load_sessions() -> dict:
    """从文件加载会话数据"""
    try:
        if SESSION_STORE_FILE.exists():
            with open(SESSION_STORE_FILE, 'r') as f:
                data = json.load(f)
                # 转换过期时间字符串回datetime对象
                for token, session in data.items():
                    session['expires_at'] = datetime.fromisoformat(session['expires_at'])
                return data
        return {}
    except Exception as e:
        logger.error(f"Error loading sessions: {e}")
        return {}


def _serialize_user_data(user_data: dict) -> dict:
    """序列化用户数据，移除不可JSON化的对象"""
    serialized = {}
    for key, value in user_data.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, (str, int, float, bool, type(None))):
            serialized[key] = value
        # 跳过其他复杂对象
    return serialized


def _save_sessions(sessions: dict):
    """保存会话数据到文件"""
    try:
        # 确保目录存在
        SESSION_STORE_FILE.parent.mkdir(exist_ok=True)

        # 转换datetime对象为字符串用于JSON序列化
        serializable_sessions = {}
        for token, session in sessions.items():
            serializable_sessions[token] = {
                'user': _serialize_user_data(session['user']),
                'expires_at': session['expires_at'].isoformat()
            }

        with open(SESSION_STORE_FILE, 'w') as f:
            json.dump(serializable_sessions, f)
    except Exception as e:
        logger.error(f"Error saving sessions: {e}")


def generate_session_token(user_data: dict) -> str:
    """生成会话令牌"""
    # 使用用户ID和时间戳生成唯一令牌
    user_id = str(user_data.get('id', ''))
    timestamp = str(int(time.time()))
    token_raw = f"{user_id}:{timestamp}:{app_config.secret_key}"
    return hashlib.sha256(token_raw.encode()).hexdigest()[:32]


def save_session_to_store(token: str, user_data: dict, expires_hours: int = 24):
    """保存会话到文件存储"""
    expires_at = datetime.now() + timedelta(hours=expires_hours)

    # 加载现有会话
    sessions = _load_sessions()

    # 添加新会话
    sessions[token] = {
        'user': user_data,
        'expires_at': expires_at
    }

    # 保存到文件
    _save_sessions(sessions)


def restore_session_from_store(token: str) -> dict | None:
    """从文件存储恢复会话"""
    sessions = _load_sessions()

    if token not in sessions:
        return None

    session = sessions[token]
    if datetime.now() > session['expires_at']:
        # 会话已过期，删除并保存
        del sessions[token]
        _save_sessions(sessions)
        return None

    return session['user']


def cleanup_expired_sessions():
    """清理过期会话"""
    sessions = _load_sessions()
    now = datetime.now()
    expired_tokens = [
        token for token, session in sessions.items()
        if now > session['expires_at']
    ]

    if expired_tokens:
        for token in expired_tokens:
            del sessions[token]
        _save_sessions(sessions)


def init_session_state():
    """初始化session state"""
    # 初始化用户状态
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    if 'page_selected' not in st.session_state:
        st.session_state.page_selected = '📈 仪表盘'
    if 'remembered_username' not in st.session_state:
        st.session_state.remembered_username = ''

    # 初始化会话ID（用于跟踪会话）
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())

    # 尝试从URL参数恢复会话（只恢复一次）
    query_params = st.query_params
    if 'session_token' in query_params and not st.session_state.get('user') and not st.session_state.get('session_restored'):
        session_token = query_params['session_token']
        restored_user = restore_session_from_store(session_token)
        if restored_user:
            st.session_state.user = restored_user
            st.session_state.current_page = 'dashboard'
            st.session_state.page_selected = '📈 仪表盘'
            st.session_state.session_restored = True
            # 清理URL参数（不触发rerun以避免死循环）
            try:
                del query_params['session_token']
            except:
                pass

    # 调试：打印session state状态
    if st.session_state.get('user'):
        st.session_state._login_debug = f"已登录用户: {st.session_state.user['real_name']}"
    else:
        st.session_state._login_debug = "未登录"


def show_login():
    """显示登录页面"""
    # 确保初始化session state
    init_session_state()

    st.title("📊 政府投资基金投向评分系统")
    st.subheader("用户登录")

    # 办法说明
    st.markdown("""
    <div style="padding: 15px; background-color: #f0f8ff; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #4472C4;">
        <p style="margin: 0; font-size: 14px; color: #333;">
            📖 <b>评分依据</b>：本系统参照《政府投资基金投向评价管理办法（试行）》进行设计<br>
            <a href="https://zfxxgk.ndrc.gov.cn/web/iteminfo.jsp?id=20590" target="_blank" style="color: #4472C4; text-decoration: none; font-weight: 500;">
                🔗 查看《政府投资基金投向评价管理办法（试行）》全文
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        # 从session_state中获取记住的用户名
        remembered_username = st.session_state.get('remembered_username', '')
        username = st.text_input("用户名", placeholder="请输入用户名", value=remembered_username, key="login_username")
        password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")
        remember_me = st.checkbox("记住用户名", value=False, key="remember_me")
        submitted = st.form_submit_button("登录", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("请输入用户名和密码")
                return

            user = user_service.authenticate(username, password)
            if user:
                st.session_state.user = user
                st.session_state.current_page = 'dashboard'
                st.session_state.page_selected = '📈 仪表盘'

                # 生成并保存会话令牌
                session_token = generate_session_token(user)
                save_session_to_store(session_token, user)
                st.session_state.session_token = session_token

                # 如果选择记住用户名，则保存到session_state
                if remember_me:
                    st.session_state.remembered_username = username
                else:
                    st.session_state.remembered_username = ''

                st.success(f"欢迎回来，{user['real_name']}！")
                # 兼容旧版streamlit
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.error("用户名或密码错误")

    st.info("💡 默认管理员账号：admin / admin123")

    # 添加登录状态说明
    st.caption("💡 登录后请保持浏览器标签页打开。如需刷新页面，请使用浏览器的刷新按钮而不是重新打开网址。")

    # 显示会话状态（调试用）
    if '_login_debug' in st.session_state:
        st.caption(f"🔍 会话状态: {st.session_state._login_debug}")

    # 显示正确的访问地址
    st.markdown("""
    <div style="padding: 10px; background-color: #e8f5e9; border-radius: 5px; margin-top: 20px;">
        <p style="margin: 0; font-size: 14px; color: #2e7d32;">
            🌐 <b>访问地址</b>：
            <a href="http://localhost:8502" target="_blank" style="color: #1565c0; text-decoration: none; font-weight: 500;">http://localhost:8502</a>
            或
            <a href="http://192.168.1.104:8502" target="_blank" style="color: #1565c0; text-decoration: none; font-weight: 500;">http://192.168.1.104:8502</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.title(f"📊 {app_config.app_name}")
        st.divider()

        # 用户信息
        user = st.session_state.get('user')
        if user:
            st.write(f"**用户**: {user['real_name']}")
            st.write(f"**角色**: {user_service.get_role_name(user['role'])}")
            if user.get('department'):
                st.write(f"**部门**: {user['department']}")
            st.divider()

            # 导航菜单 - 按正确顺序定义
            pages = {
                'dashboard': '📈 仪表盘',
                'funds': '💰 基金管理',
                'investments': '📁 投资管理',
                'scoring': '📝 评分录入',
                'results': '📊 结果展示',
                'statistics': '📉 统计分析',
                'admin': '⚙️ 系统管理'
            }

            # 根据角色显示不同的菜单（按正确的显示顺序）
            available_pages = ['dashboard']

            # 基金管理
            if user_service.check_permission(user['role'], 'can_view_all'):
                available_pages.append('funds')

            # 投资管理
            if user_service.check_permission(user['role'], 'can_view_all'):
                available_pages.append('investments')

            # 评分录入
            if user_service.check_permission(user['role'], 'can_score'):
                available_pages.append('scoring')

            # 结果展示
            if user_service.check_permission(user['role'], 'can_view_all'):
                available_pages.append('results')

            # 统计分析
            if user_service.check_permission(user['role'], 'can_view_statistics'):
                available_pages.append('statistics')

            # 系统管理
            if user_service.check_permission(user['role'], 'can_manage_users'):
                available_pages.append('admin')

            # 创建页面选择器
            page_labels = {k: pages[k] for k in available_pages}
            # 获取当前页面对应的标签
            current_label = page_labels.get(st.session_state.current_page, list(page_labels.values())[0])
            # 使用索引来避免每次渲染都更新
            label_list = list(page_labels.values())
            default_index = label_list.index(current_label) if current_label in label_list else 0

            selected_label = st.radio(
                "选择功能",
                label_list,
                index=default_index,
                label_visibility="collapsed",
                key="nav_radio"  # 添加固定的key
            )

            # 立即处理页面跳转（解决第一次点击无反应的问题）
            if selected_label != st.session_state.get('page_selected'):
                for page_code, page_label in page_labels.items():
                    if page_label == selected_label:
                        st.session_state.current_page = page_code
                        st.session_state.page_selected = page_label
                        # 立即刷新页面
                        try:
                            st.rerun()
                        except AttributeError:
                            st.experimental_rerun()
                        break

            st.divider()

            # 登出按钮
            if st.button("退出登录", use_container_width=True):
                # 只清除用户相关的session state
                for key in ['user', 'current_page', 'page_selected']:
                    if key in st.session_state:
                        del st.session_state[key]
                # 兼容旧版streamlit
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()


def show_dashboard():
    """显示仪表盘"""
    st.title("📈 评分概览")

    # 添加办法链接和访问地址
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="padding: 10px; background-color: #f0f8ff; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 13px; color: #555;">
                📖 <b>评分依据</b>：<a href="https://zfxxgk.ndrc.gov.cn/web/iteminfo.jsp?id=20590" target="_blank" style="color: #4472C4;">《政府投资基金投向评价管理办法（试行）》</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="padding: 10px; background-color: #e8f5e9; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 13px; color: #2e7d32;">
                🌐 <b>访问地址</b>：<br/>
                <a href="http://localhost:8502" target="_blank" style="color: #1565c0; text-decoration: none; font-weight: 500;">http://localhost:8502</a><br/>
                <a href="http://192.168.1.104:8502" target="_blank" style="color: #1565c0; text-decoration: none; font-weight: 500;">http://192.168.1.104:8502</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 统计卡片（使用基金数据）
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_funds = fund_service.count_funds()
        st.metric("总基金数", total_funds)

    with col2:
        # 统计已评分的基金数量（已计算总分的）
        from app.utils.database import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM fund_total_scores")
                result = cursor.fetchone()
                scored_funds = result['count'] if result else 0
        st.metric("已评分基金", scored_funds)

    with col3:
        grade_dist = scoring_service.get_fund_grade_distribution()
        excellent_count = grade_dist.get('excellent', 0)
        st.metric("优秀基金数", excellent_count)

    with col4:
        total = sum(grade_dist.values())
        excellent_rate = (excellent_count / total * 100) if total > 0 else 0
        st.metric("优秀率", f"{excellent_rate:.1f}%")

    st.divider()

    # 维度平均分
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("等级分布")
        if grade_dist:
            import pandas as pd
            df = pd.DataFrame([
                {'等级': '优秀', '数量': grade_dist.get('excellent', 0)},
                {'等级': '良好', '数量': grade_dist.get('good', 0)},
                {'等级': '合格', '数量': grade_dist.get('qualified', 0)},
                {'等级': '不合格', '数量': grade_dist.get('unqualified', 0)}
            ])
            st.bar_chart(df.set_index('等级'))
        else:
            st.info("暂无评分数据")

    with col2:
        st.subheader("维度平均分")
        dimension_avg = scoring_service.get_fund_dimension_averages()
        if dimension_avg:
            import pandas as pd
            df = pd.DataFrame([
                {'维度': '政策符合性', '平均分': dimension_avg.get('POLICY', 0)},
                {'维度': '优化生产力布局', '平均分': dimension_avg.get('LAYOUT', 0)},
                {'维度': '政策执行能力', '平均分': dimension_avg.get('EXECUTION', 0)}
            ])
            st.bar_chart(df.set_index('维度'))
        else:
            st.info("暂无评分数据")

    # 最近基金
    st.subheader("基金评分状态")
    # 获取所有基金及其评分状态
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT f.fund_code, f.fund_name, f.status,
                       COALESCE(ft.total_score, 0) as total_score,
                       ft.grade,
                       f.created_at
                FROM funds f
                LEFT JOIN fund_total_scores ft ON f.id = ft.fund_id
                WHERE f.status IN ('active', 'completed')
                ORDER BY f.created_at DESC
                LIMIT 10
            """)
            funds = cursor.fetchall()

    if funds:
        import pandas as pd
        df = pd.DataFrame(funds)
        df['创建时间'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        df['状态'] = df['status'].map({'active': '活跃', 'completed': '已完成'})
        df['总分'] = df['total_score'].apply(lambda x: f"{x:.2f}" if x > 0 else '-')
        df['等级'] = df['grade'].map({
            'excellent': '优秀',
            'good': '良好',
            'qualified': '合格',
            'unqualified': '不合格'
        }).fillna('-')
        st.dataframe(
            df[['fund_code', 'fund_name', '总分', '等级', '状态', '创建时间']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无基金数据")


def show_fund_management():
    """显示基金管理页面"""
    st.title("💰 基金管理")

    # 创建基金按钮
    with st.expander("➕ 创建新基金", expanded=False):
        with st.form("create_fund_form"):
            col1, col2 = st.columns(2)
            with col1:
                fund_code = st.text_input("基金编码*", placeholder="如: FUND001")
                fund_name = st.text_input("基金名称*", placeholder="输入基金名称")
                fund_manager = st.text_input("基金管理人*", placeholder="输入基金管理人")
            with col2:
                total_amount = st.number_input("基金总规模（万元）", min_value=0.0, value=0.0, step=1000.0)
                establishment_date = st.date_input("成立日期")
                fund_type = st.selectbox("基金类型", ["产业投资基金", "创业投资基金", "并购投资基金", "其他"])

            col3, col4 = st.columns(2)
            with col3:
                region = st.text_input("注册地区", placeholder="如: 北京市")
                department = st.text_input("主管部门", placeholder="如: 财政局")
            with col4:
                description = st.text_area("基金描述", placeholder="输入基金描述")

            submitted = st.form_submit_button("创建基金", use_container_width=True, type="primary")

            if submitted:
                if not fund_code or not fund_name or not fund_manager:
                    st.error("基金编码、基金名称和基金管理人为必填项")
                else:
                    user = st.session_state.get('user')

                    fund_data = {
                        'fund_code': fund_code,
                        'fund_name': fund_name,
                        'fund_manager': fund_manager,
                        'total_amount': total_amount if total_amount > 0 else None,
                        'establishment_date': establishment_date,
                        'fund_type': fund_type,
                        'region': region if region else None,
                        'department': department if department else None,
                        'description': description if description else None,
                        'status': 'active',
                        'created_by': user['id'] if user else 1
                    }

                    result = fund_service.create_fund(fund_data)
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                    else:
                        st.error(f"❌ {result['message']}")

    st.divider()

    # 筛选条件
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("状态", ["全部", "draft", "active", "completed", "archived"], index=0, key="fm_status")
    with col2:
        region_filter = st.text_input("地区", key="fm_region")
    with col3:
        fund_type_filter = st.text_input("基金类型", key="fm_type")

    # 获取基金列表
    status = None if status_filter == "全部" else status_filter
    funds = fund_service.list_funds(
        status=status,
        region=region_filter if region_filter else None,
        fund_type=fund_type_filter if fund_type_filter else None
    )

    # 显示基金列表
    if funds:
        import pandas as pd
        df = pd.DataFrame(funds)
        df['创建时间'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')

        st.dataframe(
            df[['fund_code', 'fund_name', 'fund_manager', 'total_amount', 'fund_type', 'region', 'status', '创建时间']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无基金数据，请先创建基金")


def show_investment_management():
    """显示投资管理页面"""
    st.title("📁 投资管理")

    # 首先选择基金
    funds = fund_service.list_funds(status='active')

    if not funds:
        st.warning("暂无可用基金，请先创建基金")
        return

    # 基金选择
    fund_options = {f"{f['fund_code']} - {f['fund_name']}": f['id'] for f in funds}
    selected_fund = st.selectbox("选择基金", list(fund_options.keys()))

    if not selected_fund:
        return

    fund_id = fund_options[selected_fund]

    st.divider()

    # 创建投资按钮
    with st.expander("➕ 创建新投资项目", expanded=False):
        with st.form("create_investment_form"):
            col1, col2 = st.columns(2)
            with col1:
                investment_code = st.text_input("投资编码*", placeholder="如: INV001")
                investment_name = st.text_input("投资名称*", placeholder="输入投资名称")
            with col2:
                investment_amount = st.number_input("投资金额（万元）", min_value=0.0, value=0.0, step=100.0)
                investment_date = st.date_input("投资日期")

            col3, col4 = st.columns(2)
            with col3:
                industry = st.text_input("投向行业", placeholder="如: 新能源")
                investment_stage = st.selectbox("投资阶段", ["seed", "early", "growth", "mature"], index=1)
            with col4:
                description = st.text_area("投资描述", placeholder="输入投资描述")

            submitted = st.form_submit_button("创建投资", use_container_width=True, type="primary")

            if submitted:
                if not investment_code or not investment_name:
                    st.error("投资编码和投资名称为必填项")
                else:
                    user = st.session_state.get('user')

                    investment_data = {
                        'fund_id': fund_id,
                        'investment_code': investment_code,
                        'investment_name': investment_name,
                        'investment_amount': investment_amount if investment_amount > 0 else None,
                        'investment_date': investment_date,
                        'industry': industry if industry else None,
                        'investment_stage': investment_stage,
                        'description': description if description else None,
                        'status': 'submitted',
                        'created_by': user['id'] if user else 1
                    }

                    result = investment_service.create_investment(investment_data)
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                    else:
                        st.error(f"❌ {result['message']}")

    st.divider()

    # 筛选条件
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("状态", ["全部", "draft", "submitted", "scoring", "completed", "archived"], index=2, key="im_status")
    with col2:
        industry_filter = st.text_input("行业", key="im_industry")

    # 获取投资列表
    status = None if status_filter == "全部" else status_filter
    investments = investment_service.list_investments(
        fund_id=fund_id,
        status=status,
        industry=industry_filter if industry_filter else None
    )

    # 显示投资列表
    if investments:
        import pandas as pd
        df = pd.DataFrame(investments)
        df['创建时间'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')

        st.dataframe(
            df[['investment_code', 'investment_name', 'investment_amount', 'industry', 'investment_stage', 'status', '创建时间']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("该基金下暂无投资数据，请先创建投资")


def show_project_management():
    """显示项目管理页面"""
    st.title("📁 项目管理")

    # 创建项目按钮
    with st.expander("➕ 创建新项目", expanded=False):
        with st.form("create_project_form"):
            col1, col2 = st.columns(2)
            with col1:
                project_code = st.text_input("项目编码*", placeholder="如: PRJ001")
                project_name = st.text_input("项目名称*", placeholder="输入项目名称")
                fund_name = st.text_input("基金名称", placeholder="输入基金名称")
            with col2:
                fund_manager = st.text_input("基金管理人", placeholder="输入基金管理人")
                investment_amount = st.number_input("投资金额（万元）", min_value=0.0, value=0.0, step=100.0)
                investment_date = st.date_input("投资日期")

            col3, col4 = st.columns(2)
            with col3:
                region = st.text_input("地区", placeholder="如: 北京市")
                industry = st.text_input("行业", placeholder="如: 新能源")
            with col4:
                project_stage = st.selectbox("项目阶段", ["seed", "early", "growth", "mature"], index=1)
                description = st.text_area("项目描述", placeholder="输入项目描述")

            submitted = st.form_submit_button("创建项目", use_container_width=True, type="primary")

            if submitted:
                if not project_code or not project_name:
                    st.error("项目编码和项目名称为必填项")
                else:
                    from datetime import datetime
                    user = st.session_state.get('user')

                    project_data = {
                        'project_code': project_code,
                        'project_name': project_name,
                        'fund_name': fund_name if fund_name else None,
                        'fund_manager': fund_manager if fund_manager else None,
                        'investment_amount': investment_amount if investment_amount > 0 else None,
                        'investment_date': investment_date,
                        'region': region if region else None,
                        'industry': industry if industry else None,
                        'project_stage': project_stage,
                        'description': description if description else None,
                        'status': 'submitted',
                        'created_by': user['id'] if user else 1
                    }

                    result = project_service.create_project(project_data)
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                    else:
                        st.error(f"❌ {result['message']}")

    st.divider()

    # 筛选条件
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("状态", ["全部", "draft", "submitted", "scoring", "completed", "archived"], index=0, key="pm_status")
    with col2:
        region_filter = st.text_input("地区", key="pm_region")
    with col3:
        industry_filter = st.text_input("行业", key="pm_industry")

    # 获取项目列表
    status = None if status_filter == "全部" else status_filter
    projects = project_service.list_projects(
        status=status,
        region=region_filter if region_filter else None,
        industry=industry_filter if industry_filter else None
    )

    # 显示项目列表
    if projects:
        import pandas as pd
        df = pd.DataFrame(projects)
        df['创建时间'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')

        st.dataframe(
            df[['project_code', 'project_name', 'fund_name', 'region', 'industry', 'status', '创建时间']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无项目数据，请先创建项目")


def show_scoring():
    """显示评分录入页面"""
    # 标题和文件链接
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("📝 评分录入")
    with col2:
        # 参考文件链接
        st.markdown("""
        <div style="text-align: right; padding-top: 1rem;">
            <a href="https://zfxxgk.ndrc.gov.cn/web/iteminfo.jsp?id=20590" target="_blank" style="text-decoration: none;">
                📄 查看管理办法
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 获取待评分基金
    funds = fund_service.list_funds(status='active')

    if not funds:
        st.warning("暂无待评分基金")
        return

    # 基金选择
    fund_options = {f"{f['fund_code']} - {f['fund_name']}": f['id'] for f in funds}
    selected = st.selectbox("选择基金", list(fund_options.keys()))

    if not selected:
        return

    fund_id = fund_options[selected]
    fund = fund_service.get_fund(fund_id)

    # 显示基金信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**基金规模**: {fund.get('total_amount', 0)} 万元")
    with col2:
        st.info(f"**基金管理人**: {fund.get('fund_manager', '-')}")
    with col3:
        st.info(f"**基金类型**: {fund.get('fund_type', '-')}")

    st.divider()

    # 获取评分结构
    from config.scoring_rules import SCORING_DIMENSIONS
    structure = scoring_service.get_scoring_structure()

    # 按维度显示评分表单
    st.subheader("评分指标")

    # 获取当前评分
    current_scores = scoring_service.get_fund_scoring_detail(fund_id)

    # 为每个指标创建评分选项（包括子指标）
    scoring_options = {}

    for dim_code, dimension in SCORING_DIMENSIONS.items():
        for indicator in dimension['indicators']:
            # 处理父指标（包含子指标）- 为子指标生成选项
            if indicator.get('type') == 'parent':
                sub_indicators = indicator.get('sub_indicators', [])
                for sub in sub_indicators:
                    options = []
                    if 'scoring_guide' in sub and sub['scoring_guide']:
                        # 将评分指南转换为选项
                        for score_range, description in sub['scoring_guide'].items():
                            # 解析分数范围
                            if '-' in score_range:
                                min_score, max_score = score_range.split('-')
                                options.append({
                                    'label': f"{description} ({min_score}-{max_score}分)",
                                    'score': float(max_score),  # 使用最高分
                                    'description': description
                                })
                            else:
                                # 单个分数
                                options.append({
                                    'label': f"{description} ({score_range}分)",
                                    'score': float(score_range),
                                    'description': description
                                })
                    else:
                        # 如果没有评分指南，提供0到最高分的整数选项
                        max_score = int(sub['max_score'])
                        for i in range(max_score + 1):
                            options.append({
                                'label': f"{i}分",
                                'score': float(i),
                                'description': f"{i}分"
                            })

                    # 按分数降序排列
                    options.sort(key=lambda x: x['score'], reverse=True)
                    scoring_options[sub['code']] = options
                # 父指标本身不创建评分选项，继续下一个
                continue

            # 处理叶子指标（实际评分）
            options = []
            if 'scoring_guide' in indicator and indicator['scoring_guide']:
                # 将评分指南转换为选项
                for score_range, description in indicator['scoring_guide'].items():
                    # 解析分数范围
                    if '-' in score_range:
                        min_score, max_score = score_range.split('-')
                        options.append({
                            'label': f"{description} ({min_score}-{max_score}分)",
                            'score': float(max_score),  # 使用最高分
                            'description': description
                        })
                    else:
                        # 单个分数
                        options.append({
                            'label': f"{description} ({score_range}分)",
                            'score': float(score_range),
                            'description': description
                        })
            else:
                # 如果没有评分指南，提供0到最高分的整数选项
                max_score = int(indicator['max_score'])
                for i in range(max_score + 1):
                    options.append({
                        'label': f"{i}分",
                        'score': float(i),
                        'description': f"{i}分"
                    })

            # 按分数降序排列
            options.sort(key=lambda x: x['score'], reverse=True)
            scoring_options[indicator['code']] = options

    # 创建回调函数用于自动保存单个评分
    def save_single_score(fund_id, indicator_code, dim_code, user_id):
        """保存单个评分的回调函数（接收参数）"""
        # 添加调试日志
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"save_single_score 被调用: fund_id={fund_id}, indicator_code={indicator_code}")

        # 从selectbox的key直接获取当前选中的索引
        selectbox_key = f"score_{fund_id}_{indicator_code}"
        if selectbox_key in st.session_state:
            selected_index = st.session_state[selectbox_key]

            # 获取该指标对应的所有选项
            indicator_key = f"_options_{fund_id}_{indicator_code}"
            if indicator_key in st.session_state:
                options = st.session_state[indicator_key]
                score_value = options[selected_index]['score']

                # 获取dimension_id和indicator_id
                from app.utils.database import get_db_connection
                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT id FROM scoring_dimensions WHERE dimension_code = %s",
                            (dim_code,)
                        )
                        dim_result = cursor.fetchone()
                        if dim_result:
                            dimension_id = dim_result['id']

                            cursor.execute(
                                "SELECT id FROM scoring_indicators WHERE indicator_code = %s",
                                (indicator_code,)
                            )
                            ind_result = cursor.fetchone()
                            if ind_result:
                                indicator_id = ind_result['id']

                                # 保存评分
                                from decimal import Decimal
                                logger.info(f"准备保存评分: fund_id={fund_id}, indicator_code={indicator_code}, score={score_value}")
                                result = scoring_service.submit_fund_indicator_score(
                                    fund_id=fund_id,
                                    dimension_id=dimension_id,
                                    indicator_id=indicator_id,
                                    raw_score=Decimal(str(score_value)),
                                    scorer_id=user_id,
                                    scorer_comment=None
                                )

                                logger.info(f"保存结果: {result}")
                                if result['success']:
                                    st.session_state[f"_last_saved_{indicator_code}"] = f"✓ 已保存：{score_value}分"
                                    st.session_state[f"score_value_{fund_id}_{indicator_code}"] = score_value
                                else:
                                    logger.error(f"保存失败: {result.get('message')}")
                                    st.session_state[f"_last_saved_{indicator_code}"] = f"❌ 保存失败: {result.get('message')}"
                            else:
                                logger.error(f"未找到indicator: indicator_code={indicator_code}")
                        else:
                            logger.error(f"未找到dimension: dim_code={dim_code}")
            else:
                logger.error(f"未找到options: {indicator_key}")
        else:
            logger.error(f"未找到selectbox值: {selectbox_key}")

    # 创建评分表单（移除form wrapper，使用callbacks自动保存）
    user = st.session_state.user

    # 检查当前已评分数量
    from app.utils.database import get_db_connection
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(DISTINCT indicator_id) as scored_count FROM fund_scores WHERE fund_id = %s",
                (fund_id,)
            )
            scored_count_result = cursor.fetchone()
            current_scored_count = scored_count_result['scored_count'] if scored_count_result else 0

    # 添加提示信息
    st.info(f"💡 **自动保存已启用**：每次选择评分选项后会自动保存到数据库。当前已完成 {current_scored_count}/26 个指标的评分。全部评分完成后，请点击底部的「计算总分」按钮。")

    # 维度计数器
    dim_idx = 0
    for dim_code, dimension in SCORING_DIMENSIONS.items():
            dim_idx += 1
            st.markdown(f"""
                <div style="font-size: 20px; font-weight: 600; color: #1f77b4; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e0e0e0;">
                    {dim_idx}. {dimension['name']}（权重 {dimension['weight']}%，满分 {dimension['max_score']} 分）
                </div>
            """, unsafe_allow_html=True)

            # 指标计数器
            ind_idx = 0
            for indicator in dimension['indicators']:
                ind_idx += 1
                # 处理父指标（包含子指标）
                if indicator.get('type') == 'parent':
                    # 显示父指标标题栏
                    st.markdown(f"""
                        <div style="font-size: 18px; font-weight: 500; color: #333; margin-top: 10px; margin-bottom: 5px;">
                            📊 {dim_idx}.{ind_idx} {indicator['name']}
                        </div>
                    """, unsafe_allow_html=True)

                    # 计算子指标汇总得分
                    sub_indicators = indicator.get('sub_indicators', [])
                    total_sub_score = 0.0
                    for sub in sub_indicators:
                        score_key = f"score_value_{fund_id}_{sub['code']}"
                        if score_key in st.session_state:
                            total_sub_score += st.session_state[score_key]

                    # 显示父指标汇总信息
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.caption(f"满分: {indicator['max_score']} 分")
                    with col2:
                        # 使用自定义HTML替代metric，使字体更小
                        st.markdown(f"""
                            <div style="font-size: 14px; line-height: 1.2; padding: 5px 0;">
                                <span style="color: #666; font-size: 12px;">小计得分：</span>
                                <span style="color: #1f77b4; font-weight: 600; font-size: 14px;">{total_sub_score:.1f}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        completion = len([s for s in sub_indicators if f"score_value_{fund_id}_{s['code']}" in st.session_state])
                        st.caption(f"完成度: {completion}/{len(sub_indicators)}")

                    # 显示子指标
                    sub_idx = 0
                    for sub in sub_indicators:
                        sub_idx += 1
                        options = scoring_options.get(sub['code'], [])

                        # 获取当前选择的索引
                        current_score = 0
                        if current_scores.get('success') and current_scores['data']['dimensions']:
                            for dim_data in current_scores['data']['dimensions'].values():
                                for ind in dim_data['indicators']:
                                    if ind['code'] == sub['code']:
                                        current_score = ind['score']
                                        break

                        # 找到当前分数对应的索引（精确匹配）
                        default_index = 0
                        score_found = False
                        for i, opt in enumerate(options):
                            if opt['score'] == current_score:
                                default_index = i
                                score_found = True
                                break

                        # 如果没有找到匹配的分数，使用第一个选项
                        if not score_found and options:
                            default_index = 0
                        # 如果当前分数为0（未评分），查找第一个选项
                        elif current_score == 0 and options:
                            default_index = 0

                        # 子指标标题栏（缩进显示）
                        st.markdown(f"""
                            <div style="font-size: 16px; font-weight: 400; color: #555; margin-left: 40px; margin-top: 5px; margin-bottom: 8px;">
                                └─ {dim_idx}.{ind_idx}.{sub_idx} {sub['name']}（满分 {sub['max_score']} 分）
                            </div>
                        """, unsafe_allow_html=True)

                        # 将选项存储到session_state，供回调函数使用
                        st.session_state[f"_options_{fund_id}_{sub['code']}"] = options

                        # 创建选项标签列表（用于显示）
                        option_labels = [opt['label'] for opt in options]

                        # 使用columns实现缩进（与标题40px缩进保持一致）
                        col_space, col_content = st.columns([0.08, 0.92])
                        with col_content:
                            # 使用selectbox让用户选择评分等级（带自动保存）
                            selected_index = st.selectbox(
                                f"_{sub['code']}",  # 使用下划线前缀使标签最小化
                                options=range(len(options)),
                                format_func=lambda i: option_labels[i],
                                index=default_index,
                                key=f"score_{fund_id}_{sub['code']}",
                                on_change=save_single_score,
                                args=(fund_id, sub['code'], dim_code, user['id']),
                                label_visibility="collapsed"  # 隐藏标签
                            )

                        # 将选择的分数存储到session_state
                        selected_option = options[selected_index]
                        st.session_state[f"score_value_{fund_id}_{sub['code']}"] = selected_option['score']

                        # 显示保存状态
                        saved_key = f"_last_saved_{sub['code']}"
                        if saved_key in st.session_state:
                            st.caption(st.session_state[saved_key])

                    st.markdown("<br>", unsafe_allow_html=True)

                # 处理叶子指标（直接评分）
                else:
                    options = scoring_options.get(indicator['code'], [])

                    # 获取当前选择的索引
                    current_score = 0
                    if current_scores.get('success') and current_scores['data']['dimensions']:
                        for dim_data in current_scores['data']['dimensions'].values():
                            for ind in dim_data['indicators']:
                                if ind['code'] == indicator['code']:
                                    current_score = ind['score']
                                    break

                    # 找到当前分数对应的索引（精确匹配）
                    default_index = 0
                    score_found = False
                    for i, opt in enumerate(options):
                        if opt['score'] == current_score:
                            default_index = i
                            score_found = True
                            break

                    # 如果没有找到匹配的分数，使用第一个选项
                    if not score_found and options:
                        default_index = 0
                    # 如果当前分数为0（未评分），查找第一个选项
                    elif current_score == 0 and options:
                        default_index = 0

                    # 叶子指标标题栏（与父指标样式一致）
                    st.markdown(f"""
                        <div style="font-size: 18px; font-weight: 500; color: #333; margin-top: 15px; margin-bottom: 10px;">
                            {dim_idx}.{ind_idx} {indicator['name']}（满分 {indicator['max_score']} 分）
                        </div>
                    """, unsafe_allow_html=True)

                    # 将选项存储到session_state，供回调函数使用
                    st.session_state[f"_options_{fund_id}_{indicator['code']}"] = options

                    # 创建选项标签列表（用于显示）
                    option_labels = [opt['label'] for opt in options]

                    # 使用selectbox让用户选择评分等级（带自动保存）
                    selected_index = st.selectbox(
                        f"_{indicator['code']}",  # 使用下划线前缀使标签最小化
                        options=range(len(options)),
                        format_func=lambda i: option_labels[i],
                        index=default_index,
                        key=f"score_{fund_id}_{indicator['code']}",
                        on_change=save_single_score,
                        args=(fund_id, indicator['code'], dim_code, user['id']),
                        label_visibility="collapsed"  # 隐藏标签
                    )

                    # 将选择的分数存储到session_state
                    selected_option = options[selected_index]
                    st.session_state[f"score_value_{fund_id}_{indicator['code']}"] = selected_option['score']

                    # 显示保存状态
                    saved_key = f"_last_saved_{indicator['code']}"
                    if saved_key in st.session_state:
                        st.caption(st.session_state[saved_key])

            st.divider()

    # 计算总分按钮（替代原来的保存评分按钮）
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🧮 计算总分", use_container_width=True, type="primary"):
            with st.spinner("正在计算总分..."):
                result = scoring_service.calculate_fund_total_score(fund_id)
                if result['success']:
                    st.success(f"""
                        ✅ **计算完成！**

                        - **总分**：{result['data']['total_score']:.2f} 分
                        - **等级**：{result['data']['grade_name']}
                        - **政策符合性**：{result.get('data', {}).get('policy_score', 0):.2f} 分
                        - **优化生产力布局**：{result.get('data', {}).get('layout_score', 0):.2f} 分
                        - **政策执行能力**：{result.get('data', {}).get('execution_score', 0):.2f} 分
                    """)
                    st.balloons()
                else:
                    st.error(f"❌ {result['message']}")


def save_scores_with_options(fund_id: int, structure: dict, scorer_id: int):
    """保存评分（使用选项方式）- 支持层级指标"""
    from decimal import Decimal
    from config.scoring_rules import SCORING_DIMENSIONS

    success_count = 0
    error_count = 0

    # 收集所有需要保存的指标评分
    scores_to_save = []

    with st.spinner("正在保存评分..."):
        for dim_code, dimension in SCORING_DIMENSIONS.items():
            for indicator in dimension['indicators']:
                # 处理父指标：收集子指标评分
                if indicator.get('type') == 'parent':
                    sub_indicators = indicator.get('sub_indicators', [])
                    for sub in sub_indicators:
                        score_key = f"score_value_{fund_id}_{sub['code']}"
                        if score_key in st.session_state:
                            scores_to_save.append({
                                'code': sub['code'],
                                'name': sub['name'],
                                'score': Decimal(str(st.session_state[score_key])),
                                'is_parent': False
                            })

                # 处理叶子指标：直接保存
                else:
                    score_key = f"score_value_{fund_id}_{indicator['code']}"
                    if score_key in st.session_state:
                        scores_to_save.append({
                            'code': indicator['code'],
                            'name': indicator['name'],
                            'score': Decimal(str(st.session_state[score_key])),
                            'is_parent': False
                        })

        # 保存所有评分
        for score_data in scores_to_save:
            # 获取dimension_id
            from app.utils.database import get_db_connection
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取dimension_id
                    cursor.execute(
                        "SELECT id FROM scoring_dimensions WHERE dimension_code = %s",
                        (dim_code,)
                    )
                    dim_result = cursor.fetchone()
                    if dim_result:
                        dimension_id = dim_result['id']

                        # 获取indicator_id
                        cursor.execute(
                            "SELECT id FROM scoring_indicators WHERE indicator_code = %s",
                            (score_data['code'],)
                        )
                        ind_result = cursor.fetchone()
                        if ind_result:
                            indicator_id = ind_result['id']

                            result = scoring_service.submit_fund_indicator_score(
                                fund_id=fund_id,
                                dimension_id=dimension_id,
                                indicator_id=indicator_id,
                                raw_score=score_data['score'],
                                scorer_id=scorer_id,
                                scorer_comment=None
                            )

                            if result['success']:
                                success_count += 1
                            else:
                                error_count += 1
                                st.error(f"{score_data['name']}: {result['message']}")

        # 保存父指标的汇总分数
        for dim_code, dimension in SCORING_DIMENSIONS.items():
            for indicator in dimension['indicators']:
                if indicator.get('type') == 'parent':
                    # 计算子指标汇总得分
                    sub_indicators = indicator.get('sub_indicators', [])
                    total_score = sum([
                        float(st.session_state.get(f"score_value_{fund_id}_{sub['code']}", 0))
                        for sub in sub_indicators
                    ])

                    # 保存父指标得分
                    from app.utils.database import get_db_connection
                    with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                "SELECT id FROM scoring_dimensions WHERE dimension_code = %s",
                                (dim_code,)
                            )
                            dim_result = cursor.fetchone()
                            if dim_result:
                                dimension_id = dim_result['id']

                                cursor.execute(
                                    "SELECT id FROM scoring_indicators WHERE indicator_code = %s",
                                    (indicator['code'],)
                                )
                                ind_result = cursor.fetchone()
                                if ind_result:
                                    indicator_id = ind_result['id']

                                    result = scoring_service.submit_fund_indicator_score(
                                        fund_id=fund_id,
                                        dimension_id=dimension_id,
                                        indicator_id=indicator_id,
                                        raw_score=Decimal(str(total_score)),
                                        scorer_id=scorer_id,
                                        scorer_comment=None
                                    )

        if error_count == 0 and success_count > 0:
            with st.spinner("正在计算总分..."):
                # 计算维度汇总
                for dim_code, dimension in structure.items():
                    from app.utils.database import get_db_connection
                    with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                "SELECT id FROM scoring_dimensions WHERE dimension_code = %s",
                                (dim_code,)
                            )
                            dim_result = cursor.fetchone()
                            if dim_result:
                                scoring_service.calculate_and_save_fund_dimension_score(
                                    fund_id, dim_result['id']
                                )

                # 计算总分
                total_result = scoring_service.calculate_fund_total_score(fund_id)

                if total_result['success']:
                    st.success(f"✅ 评分保存成功！总分: {total_result['data']['total_score']:.2f}，等级: {total_result['data']['grade_name']}")
                    st.balloons()

                    # 刷新页面以显示最新评分结果
                    import time
                    time.sleep(1)
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
                else:
                    st.warning(total_result['message'])
        elif error_count > 0:
            st.error(f"保存完成，但有 {error_count} 个指标失败")
        else:
            st.warning("没有保存任何评分，请至少选择一个评分选项")


def show_results():
    """显示结果展示页面"""
    st.title("📊 结果展示")

    # 获取已评分的基金（包括 active 和 completed 状态）
    active_funds = fund_service.list_funds(status='active') or []
    completed_funds = fund_service.list_funds(status='completed') or []
    funds = active_funds + completed_funds

    # 筛选出有评分的基金（已计算总分的或者已评满26个指标的）
    funds_with_scores = []
    for fund in funds:
        # 检查是否有总分记录（已计算总分的）
        from app.utils.database import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 首先检查是否有总分记录
                cursor.execute("SELECT COUNT(*) as count FROM fund_total_scores WHERE fund_id = %s", (fund['id'],))
                result = cursor.fetchone()
                if result and result['count'] > 0:
                    funds_with_scores.append(fund)
                    continue

                # 如果没有总分记录，检查是否已完成26个指标的评分
                cursor.execute(
                    "SELECT COUNT(DISTINCT indicator_id) as scored_count FROM fund_scores WHERE fund_id = %s",
                    (fund['id'],)
                )
                score_result = cursor.fetchone()
                if score_result and score_result['scored_count'] >= 26:
                    funds_with_scores.append(fund)

    if not funds_with_scores:
        st.info("暂无已完成评分的基金（需要完成所有26个指标评分并计算总分）")
        # 检查是否有部分完成的评分
        from app.utils.database import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT f.fund_code, f.fund_name, COUNT(DISTINCT fs.indicator_id) as scored_count
                    FROM funds f
                    LEFT JOIN fund_scores fs ON f.id = fs.fund_id
                    WHERE f.status = 'active'
                    GROUP BY f.id
                    HAVING scored_count > 0
                    ORDER BY scored_count DESC
                """)
                partial_scores = cursor.fetchall()
                if partial_scores:
                    st.write("**部分完成评分的基金：**")
                    for row in partial_scores:
                        st.caption(f"• {row['fund_code']} - {row['fund_name']}: {row['scored_count']}/26 个指标")
        return

    # 基金选择
    fund_options = {f"{f['fund_code']} - {f['fund_name']}": f['id'] for f in funds_with_scores}
    selected = st.selectbox("选择基金", list(fund_options.keys()))

    if not selected:
        return

    fund_id = fund_options[selected]

    # 获取评分详情
    detail = scoring_service.get_fund_scoring_detail(fund_id)

    if not detail.get('success'):
        st.error(detail.get('message', '获取评分详情失败'))
        return

    data = detail['data']

    # 如果没有计算总分，显示提示
    if data.get('total_score') is None:
        st.warning("⚠️ 该基金已完成所有指标评分，但尚未计算总分。请前往「📝 评分录入」页面点击「🧮 计算总分」按钮。")
        st.divider()

    # 显示总分和等级
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("总分", f"{data['total_score']:.2f}" if data['total_score'] else "-")

    with col2:
        grade_name = data.get('grade_name') or '-'
        st.metric("等级", grade_name)

    with col3:
        rank = data.get('rank')
        st.metric("排名", f"第 {rank} 名" if rank else "-")

    with col4:
        fund = fund_service.get_fund(fund_id)
        st.metric("基金状态", fund['status'] if fund else '-')

    st.divider()

    # 下载评分报告按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 下载评分报告", type="primary", use_container_width=True):
            from core.services.export_service import export_service
            from datetime import datetime

            try:
                excel_data = export_service.export_scoring_report_excel(fund_id)

                fund = fund_service.get_fund(fund_id)
                filename = f"评分报告_{fund['fund_code']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

                st.download_button(
                    label="点击下载 Excel 文件",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"生成报告失败: {str(e)}")

    st.divider()

    # 显示各维度评分
    # 获取维度汇总数据（使用数据库中计算好的值）
    from app.utils.database import get_db_connection
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT iss.*, sd.dimension_code
                FROM fund_scoring_summary iss
                JOIN scoring_dimensions sd ON iss.dimension_id = sd.id
                WHERE iss.fund_id = %s
                ORDER BY sd.display_order
            """
            cursor.execute(sql, (fund_id,))
            dimension_summaries = {row['dimension_code']: row for row in cursor.fetchall()}

    for dim_code, dim_data in data['dimensions'].items():
        st.subheader(f"### {dim_data['name']}")

        # 使用数据库中的维度汇总数据
        if dim_code in dimension_summaries:
            dim_summary = dimension_summaries[dim_code]
            dim_total = float(dim_summary['total_score'])
            dim_weighted = float(dim_summary['weighted_total'])
        else:
            # 回退方案：计算得分（仅当数据库中没有汇总数据时）
            dim_total = sum(ind['score'] for ind in dim_data['indicators'])
            dim_weighted = sum(ind['weighted_score'] for ind in dim_data['indicators'])

        st.info(f"维度得分: {dim_total:.2f} / 加权得分: {dim_weighted:.2f}")

        # 指标列表
        import pandas as pd
        df = pd.DataFrame(dim_data['indicators'])
        df.columns = ['指标代码', '指标名称', '得分', '加权得分', '评分人', '说明', '评分时间']
        st.dataframe(df, use_container_width=True, hide_index=True)


def show_statistics():
    """显示统计分析页面"""
    st.title("📉 统计分析")

    # 等级分布
    st.subheader("等级分布")
    grade_dist = scoring_service.get_grade_distribution()

    if grade_dist:
        import pandas as pd
        df = pd.DataFrame([
            {'等级': '优秀', '数量': grade_dist.get('excellent', 0)},
            {'等级': '良好', '数量': grade_dist.get('good', 0)},
            {'等级': '合格', '数量': grade_dist.get('qualified', 0)},
            {'等级': '不合格', '数量': grade_dist.get('unqualified', 0)}
        ])
        st.bar_chart(df.set_index('等级'))
    else:
        st.info("暂无评分数据")


def show_admin():
    """显示系统管理页面"""
    st.title("⚙️ 系统管理")

    user = st.session_state.get('user')

    if not user_service.check_permission(user['role'], 'can_manage_users'):
        st.error("您没有权限访问此页面")
        return

    st.subheader("用户管理")

    # 用户列表
    users = user_service.list_users()

    if users:
        import pandas as pd
        df = pd.DataFrame(users)
        df['角色'] = df['role'].apply(user_service.get_role_name)
        st.dataframe(
            df[['username', 'real_name', 'role', 'department', 'is_active']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无用户数据")


def main():
    """应用主入口"""
    init_session_state()

    # 检查登录状态
    if not st.session_state.get('user'):
        show_login()
        return

    # 显示侧边栏
    show_sidebar()

    # 路由到对应页面
    page = st.session_state.current_page

    if page == 'dashboard':
        show_dashboard()
    elif page == 'funds':
        show_fund_management()
    elif page == 'investments':
        show_investment_management()
    elif page == 'projects':
        show_project_management()  # 保留向后兼容
    elif page == 'scoring':
        show_scoring()
    elif page == 'results':
        show_results()
    elif page == 'statistics':
        show_statistics()
    elif page == 'admin':
        show_admin()


if __name__ == "__main__":
    main()
