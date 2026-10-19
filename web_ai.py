import streamlit as st
from openai import OpenAI

# 1. 网页基本设置（必须放在最前面）
st.set_page_config(page_title="我的AI聊天室", page_icon="🤖", layout="centered")
st.title("🤖 我的专属 AI 聊天室")

# 2. 侧边栏：输入密钥和设置
with st.sidebar:
    st.header("⚙️ 控制台")
    # 让用户输入自己的密钥
    api_key = st.text_input("请输入学校 API Key", type="password", help="输入 sk- 开头的密钥")

    # 模型选择（如果学校平台报错，记得来这里改模型名）
    model_name = st.selectbox("选择模型", ["deepseek-v4-flash", "qwen3.8-27b", "deepseek-v4.1-flash"])

    # 人设设置
    system_prompt = st.text_area("AI 角色设定（System Prompt）", value="你是一个聪明、幽默的新媒体助手，说话简洁清晰。")

    # 清空聊天记录按钮
    if st.button("🧹 清空聊天记录"):
        st.session_state.messages = []
        st.rerun()

# 3. 初始化聊天记录（保存在网页内存中）
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# 4. 遍历并显示历史聊天记录
# 跳过第一条（system prompt），只显示用户和AI的对话
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. 接收用户输入并处理
# 网页底部的聊天输入框
if user_input := st.chat_input("输入你想说的话..."):
    # 如果没填密钥，给个警告
    if not api_key:
        st.warning("请先在左侧边栏输入你的 API Key！")
        st.stop()  # 停止运行后续代码

    # 把用户的话加到历史记录并显示在屏幕上
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 调用 AI 生成回复
    with st.chat_message("assistant"):
        with st.spinner("AI 正在思考中..."):
            try:
                # 初始化客户端
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://model.jsnu.edu.cn/v1"  # 学校的接口
                )

                # 发送请求
                response = client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state.messages
                )

                # 获取回复并显示
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)

                # 把 AI 的回复也存起来
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"发生错误：{e}")
                st.info("请检查：1. 密钥是否正确 2. 模型名称是否填写正确 3. 是否连接了校园网")