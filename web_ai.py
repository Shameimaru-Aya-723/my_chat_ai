import streamlit as st
from openai import OpenAI

# 1. 网页基本设置
st.set_page_config(page_title="我的AI聊天室", page_icon="🤖", layout="centered")
st.title("🤖 我的专属 AI 聊天室 (v1.1)")

# 2. 侧边栏：输入密钥和设置
with st.sidebar:
    st.header("⚙️ 控制台")

    user_api_key = st.text_input(
        "请输入 API Key (不填则使用免费体验额度)",
        type="password"
    )

    model_name = st.selectbox(
        "选择模型",
        [
            "deepseek-flash",
            "deepseek-chat",
            "deepseek-reasoner",
            "deepseek-v4.1-flash"
        ]
    )

    # 人设设置（这一项现在可以随时改了）
    system_prompt = st.text_area(
        "AI 角色设定（System Prompt）",
        value="你是一个聪明、幽默的新媒体助手，说话简洁清晰。"
    )

    # 只清空聊天记录，不动人设
    if st.button("🧹 清空聊天记录"):
        st.session_state.messages = []
        st.rerun()

# 3. 初始化聊天记录（现在这里只存用户和AI的对话，不存 System Prompt 了）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 遍历并显示历史聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. 接收用户输入并处理
if user_input := st.chat_input("输入你想说的话..."):

    # 判断用谁的 Key
    if user_api_key:
        active_key = user_api_key
    else:
        try:
            active_key = st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            st.error("⚠️ 您未输入 API Key，且开发者未配置默认体验额度。")
            st.stop()

            # 把用户的话显示出来并加到历史记录
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 调用 AI 生成回复
    with st.chat_message("assistant"):
        with st.spinner("AI 正在思考中..."):
            try:
                client = OpenAI(
                    api_key=active_key,
                    base_url="https://api.deepseek.com"
                )

                # 🌟 核心进化点 1：动态拼装发送给 AI 的列表
                # 每次发送时，把最新的左侧人设放在第一位，然后跟上最近 10 句聊天记录
                send_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages[-10:]

                # 发送请求
                response = client.chat.completions.create(
                    model=model_name,
                    messages=send_messages,
                    max_tokens=1000
                )

                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)

                # 把 AI 的回复加到本地的历史记录里
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"发生错误：{e}")