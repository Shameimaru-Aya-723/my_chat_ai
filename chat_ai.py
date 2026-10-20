from openai import OpenAI

# ==========================================
# 1. 配置你的信息（请务必修改这里）
# ==========================================
# 将引号里的内容替换为你自己在学校平台申请的密钥
MY_API_KEY = "sk-6YA7HA1BuYQt1g7JiASOdTAyZX7OzU2XKuemSy8wRz8MyPyI"

# 填入学校平台兼容的模型名称。
# 如果你不知道填什么，可以先试试 "gpt-4o" 或 "deepseek-chat"
MY_MODEL = "deepseek-v4-flash"

# ==========================================
# 2. 初始化客户端
# ==========================================
client = OpenAI(
    api_key=MY_API_KEY,
    base_url="https://model.jsnu.edu.cn/v1"  # 学校平台的固定地址
)

# 记录对话历史，这样 AI 就能记住你上一句说了什么
messages = [
    {"role": "system", "content": "你是一个聪明、幽默的新媒体助手，说话简洁清晰。"}
]

print("🤖 学校 AI 助手已上线！(输入 'quit' 退出对话)")
print("-" * 40)

# ==========================================
# 3. 开始循环对话
# ==========================================
while True:
    # 获取你输入的内容
    user_input = input("\n你: ")

    # 如果输入 quit，则退出程序
    if user_input.lower() == 'quit':
        print("下次见！")
        break

    # 如果输入为空，就跳过
    if not user_input.strip():
        continue

    # 把你的话加入历史记录
    messages.append({"role": "user", "content": user_input})

    try:
        # 向学校服务器发送请求
        print("AI 思考中...", end="", flush=True)
        response = client.chat.completions.create(
            model=MY_MODEL,
            messages=messages,
            temperature=0.7  # 0-1之间，数值越大回答越有创意，越小越严谨
        )

        # 提取 AI 的回复
        ai_reply = response.choices[0].message.content

        # 打印 AI 的回复
        print(f"\rAI: {ai_reply}")

        # 把 AI 的回复也加入历史记录，保持上下文连贯
        messages.append({"role": "assistant", "content": ai_reply})

    except Exception as e:
        # 如果报错了（比如网络断了、密钥错了），在这里提示
        print(f"\r发生错误: {e}")
        print("请检查你的 API Key 是否正确，或者网络是否连接了校园网。")
