import streamlit as st
from openai import OpenAI
import json
import datetime

st.set_page_config(page_title="我的AI聊天室", page_icon="🤖", layout="centered")
st.title("🤖 我的专属 AI 聊天室 (v1.2.5)")

# ==========================================
# 🌟 状态初始化
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt_input" not in st.session_state:
    st.session_state.system_prompt_input = "你是一个聪明、幽默的新媒体助手，说话简洁清晰。"

if "api_key_input" not in st.session_state:
    st.session_state.api_key_input = ""

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = ""

if "uploaded_file_id" not in st.session_state:
    st.session_state.uploaded_file_id = None

# 新增：用来控制页面顶部的成功提示
if "show_success_banner" not in st.session_state:
    st.session_state.show_success_banner = False

# ==========================================
# 侧边栏
# ==========================================
with st.sidebar:
    st.header("⚙️ 控制台")

    st.text_input("请输入 API Key (不填则使用体验额度)", type="password", key="api_key_input")

    model_name = st.selectbox(
        "选择模型",
        ["deepseek-flash", "deepseek-chat", "deepseek-reasoner", "deepseek-v4.1-flash"]
    )

    st.text_area("AI 角色设定（System Prompt）", key="system_prompt_input")

    st.divider()
    st.subheader("💾 数据管理")

    # 导出功能
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"records_{today_str}.json"
    json_string = json.dumps(st.session_state.messages, ensure_ascii=False, indent=4)

    st.download_button(
        label="📥 导出当前聊天记录",
        data=json_string,
        file_name=file_name,
        mime="application/json",
    )
    st.caption(f"*(文件名: {file_name})*")

    # 导入功能
    uploaded_file = st.file_uploader("📤 导入聊天记录 (.json)", type=["json"])

    if uploaded_file is not None:
        if st.session_state.uploaded_file_id != uploaded_file.id:
            try:
                imported_messages = json.load(uploaded_file)
                if isinstance(imported_messages, list):
                    st.session_state.messages = imported_messages
                    st.session_state.last_uploaded_file = uploaded_file.name
                    st.session_state.uploaded_file_id = uploaded_file.id

                    # 开启成功提示开关
                    st.session_state.show_success_banner = True
                    st.rerun()
                else:
                    st.error("文件格式错误。")
            except Exception as e:
                st.error(f"导入失败：{e}")

    if st.session_state.last_uploaded_file:
        st.caption(f"💡 上次导入的文件：`{st.session_state.last_uploaded_file}`")

    if st.button("🧹 清空所有记录"):
        st.session_state.messages = []
        st.session_state.last_uploaded_file = ""
        st.session_state.uploaded_file_id = None
        st.session_state.show_success_banner = False
        st.rerun()

# ==========================================
# 🌟 主界面聊天区域
# ==========================================

# 如果刚刚导入成功，页面顶部弹出绿色横幅，并保持到用户刷新
if st.session_state.show_success_banner:
    st.success("✅ 历史聊天记录已成功载入！请往下划查看。")
    # 顺便在屏幕右上角弹一个小提示框 (Streamlit 特有动画)
    st.toast('记录导入成功！', icon='🎉')

# 渲染所有历史聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入框
if user_input := st.chat_input("输入你想说的话..."):

    # 如果有新消息，关掉顶部的成功横幅
    st.session_state.show_success_banner = False

    active_key = st.session_state.api_key_input

    if not active_key:
        try:
            active_key = st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            st.error("⚠️ 您未输入 API Key，且开发者未配置默认体验额度。")
            st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("AI 正在思考中..."):
            try:
                client = OpenAI(api_key=active_key, base_url="https://api.deepseek.com")

                current_system_prompt = st.session_state.system_prompt_input
                send_messages = [{"role": "system", "content": current_system_prompt}] + st.session_state.messages[-10:]

                response = client.chat.completions.create(
                    model=model_name,
                    messages=send_messages,
                    max_tokens=1000
                )

                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"发生错误：{e}")