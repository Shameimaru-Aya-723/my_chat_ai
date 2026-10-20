import streamlit as st
from openai import OpenAI
import json
import datetime

st.set_page_config(page_title="我的AI聊天室", page_icon="🤖", layout="centered")
st.title("🤖 我的专属 AI 聊天室 (v1.2.9)")
st.caption("✨ 此页面由本地 AI 智能体自动更新 ✨")

# ==========================================
# 🌟 状态初始化
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt_input" not in st.session_state:
    st.session_state.system_prompt_input = "你是一个聪明、幽默的新媒体助手，说话简洁清晰。"

if "api_key_input" not in st.session_state:
    st.session_state.api_key_input = ""

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

    # 每次重新生成字符串
    json_string = json.dumps(st.session_state.messages, ensure_ascii=False, indent=4)

    if len(st.session_state.messages) > 0:
        st.download_button(
            label=f"📥 导出记录 ({len(st.session_state.messages)}条)",
            data=json_string,
            file_name=file_name,
            mime="application/json",
        )
        # 🌟 透明化展示：把要下载的内容直接印在屏幕上，你一眼就能看出是不是空的
        with st.expander("🔍 预览要导出的文件内容 (点击展开)"):
            st.code(json_string, language="json")
    else:
        st.button("📥 当前无记录可导出", disabled=True)
        st.warning("⚠️ 内存中没有聊天记录，请先聊天再导出！")

    # 导入功能
    uploaded_file = st.file_uploader("📤 导入聊天记录 (.json)", type=["json"])

    if uploaded_file is not None:
        try:
            imported_messages = json.load(uploaded_file)
            if isinstance(imported_messages, list):
                if len(imported_messages) == 0:
                    st.error("❌ 导入失败：这个文件是空的（0 条记录）。")
                else:
                    st.info(f"📦 发现文件内共有 {len(imported_messages)} 条记录。")
                    if st.button("🔥 确认覆盖并恢复记录"):
                        st.session_state.messages = imported_messages
                        st.session_state.show_success_banner = True
                        st.rerun()  # 强制刷新，让界面立刻渲染
            else:
                st.error("文件格式错误，不是列表。")
        except Exception as e:
            st.error(f"文件解析失败：{e}")

    if st.button("🧹 清空所有记录"):
        st.session_state.messages = []
        st.session_state.show_success_banner = False
        st.rerun()

# ==========================================
# 主界面
# ==========================================
if st.session_state.show_success_banner:
    st.success("✅ 历史聊天记录已成功载入！")
    st.toast('记录导入成功！', icon='🎉')

st.caption(f"当前页面聊天记录总数：{len(st.session_state.messages)} 条")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入框
if user_input := st.chat_input("输入你想说的话..."):
    st.session_state.show_success_banner = False

    active_key = st.session_state.api_key_input

    if not active_key:
        try:
            active_key = st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            st.error("⚠️ 您未输入 API Key。")
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

                # 🌟 核心修复点！强制 Rerun 一次，强制侧边栏用最新的数据重新渲染！
                st.rerun()

            except Exception as e:
                st.error(f"发生错误：{e}")
