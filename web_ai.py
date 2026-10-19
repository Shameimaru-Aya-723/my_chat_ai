import streamlit as st
from openai import OpenAI

# 1. 网页基本设置
st.set_page_config(page_title="我的AI聊天室", page_icon="🤖", layout="centered")
st.title("🤖 我的专属 AI 聊天室")

# 2. 侧边栏：输入密钥和设置
with st.sidebar:
    st.header("⚙️ 控制台")

    # 提示用户：可以填自己的，也可以不填体验
    user_api_key = st.text_input(
        "请输入 API Key (不填则使用免费体验额度)",
        type="password",
        help="填入你自己的 DeepSeek API Key"
    )

    # 模型选择
    model_name = st.selectbox("选择模型", ["deepseek-chat", "deepseek-reasoner"])

    # 人设设置
    system_prompt = st.text_area(
        "AI 角色设定（System Prompt）",
        value="你是一个聪明、幽默的新媒体助手，说话简洁清晰。"
    )

    # 清空聊天记录按钮
    if st.button("🧹 清空聊天记录"):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.rerun()

# 3. 初始化聊天记录（保存在网页内存中）
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# 4. 遍历并显示历史聊天记录
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. 接收用户输入并处理
if user_input := st.chat_input("输入你想说的话..."):

    # 【核心逻辑】判断用谁的 Key
    if user_api_key:
        active_key = user_api_key  # 如果用户填了，优先用用户的
    else:
        # 如果用户没填，尝试去 Streamlit 后台保险箱里拿你的 Key
        try:
            active_key = st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            st.error("⚠️ 您未输入 API Key，且开发者未配置默认体验额度。请自己申请 Key 填入。")
            st.stop()  # 停止运行后面的代码

    # 把用户的话加到历史记录并显示在屏幕上
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 调用 AI 生成回复
    with st.chat_message("assistant"):
        with st.spinner("AI 正在思考中..."):
            try:
                # 统一初始化客户端，使用 DeepSeek 官方接口
                client = OpenAI(
                    api_key=active_key,
                    base_url="https://api.deepseek.com"
                )

                # 发送请求
                response = client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state.messages,
                    max_tokens=1000  # 限制回复长度，防止别人恶意刷爆你的额度
                )

                # 获取回复并显示
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)

                # 把 AI 的回复也存起来
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"发生错误：{e}")
                st.info("请检查：1. 密钥是否正确 2. 是否有网络问题 3. 额度是否充足")