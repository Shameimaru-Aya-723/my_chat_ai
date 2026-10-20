import sys
import io

# 🌟 修正 Windows 终端的标准输入输出编码，彻底解决中英文报错
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

import subprocess
import os
import json
from openai import OpenAI

# ==========================================
# 1. 配置你的 API
# ==========================================
# 建议使用 DeepSeek，代码能力极强且便宜
client = OpenAI(
    api_key="sk-eb608e25c7364562a9f61e3ed1a25640",
    base_url="https://api.deepseek.com"
)


# ==========================================
# 2. 定义安全且强大的本地工具
# ==========================================
def run_terminal_command(command):
    """执行终端命令并返回结果（修复了中文编码问题）"""
    # 🚨 危险命令黑名单拦截（防止AI一怒之下删你系统）
    dangerous_commands = ["rm -rf", "del /f /s /q c:\\", "format", "shutdown"]
    for danger in dangerous_commands:
        if danger in command.lower():
            return f"⛔ 危险操作被拦截！不允许执行包含 '{danger}' 的命令。"

    try:
        # 🌟 核心修复：强制使用 utf-8 编码，并用 errors="replace" 防止乱码崩溃
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20
        )
        if result.returncode == 0:
            # 如果成功，返回标准输出
            return f"执行成功:\n{result.stdout}"
        else:
            # 如果失败，优先返回报错信息
            error_msg = result.stderr if result.stderr else result.stdout
            return f"执行失败 (返回码 {result.returncode}):\n{error_msg}"
    except subprocess.TimeoutExpired:
        return "执行超时：该命令运行时间过长（超过20秒），已强制终止。"
    except Exception as e:
        return f"执行异常: {str(e)}"


def read_file(filepath):
    """读取本地文件内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            # 如果文件太大，截断防止撑爆上下文
            if len(content) > 5000:
                return f"文件内容过长，仅返回前 5000 个字符：\n{content[:5000]}"
            return content
    except FileNotFoundError:
        return f"文件不存在: {filepath}"
    except Exception as e:
        return f"读取失败: {str(e)}"


def write_file(filepath, content):
    """写入内容到本地文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"文件 {filepath} 写入成功。"
    except Exception as e:
        return f"写入失败: {str(e)}"


# ==========================================
# 3. 组装工具列表（告诉 AI 它有哪些能力）
# ==========================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "在本地终端执行系统命令，比如运行 python 脚本、使用 git 命令、或者查看目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的完整终端命令，比如 'python app.py' 或 'dir'"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件的内容。在修改文件前，必须先读取它。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径，如 'web_ai.py'"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "将完整内容覆盖写入本地文件。通常用于修改代码或创建新文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "文件路径，如 'web_ai.py'"},
                    "content": {"type": "string", "description": "修改后的完整代码内容"}
                },
                "required": ["filepath", "content"]
            }
        }
    }
]


# ==========================================
# 4. Agent 主循环
# ==========================================
def chat_with_local_agent(user_query):
    messages = [
        {
            "role": "system",
            "content": "你是一个拥有本地系统权限的资深程序员 AI。你可以读取和写入本地文件、执行终端命令。请根据用户的指令，自主规划步骤、修改代码、运行测试。如果遇到报错，请自己读取报错并修复。不要问用户怎么做，直接调用工具完成任务。任务完成后请简短汇报。"
        },
        {"role": "user", "content": user_query}
    ]

    print(f"\n👨‍💻 你的指令: {user_query}\n" + "=" * 50)

    # 限制最多交互 8 步，防止陷入死循环无限烧钱
    for step in range(8):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"❌ API 请求失败: {e}")
            break

        msg = response.choices[0].message
        messages.append(msg)

        # 如果 AI 决定调用工具
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"🤖 [第 {step + 1} 步] AI 操作: {name}")

                if name == "run_terminal_command":
                    print(f"   💻 执行: {args['command']}")
                    result = run_terminal_command(args['command'])
                    print(f"   📤 结果: {result.strip()[:200]}")  # 只打印前200字防刷屏

                elif name == "read_file":
                    print(f"   📖 读取: {args['filepath']}")
                    result = read_file(args['filepath'])
                    print(f"   📤 结果: 已读取 {len(result)} 个字符")

                elif name == "write_file":
                    print(f"   📝 修改/创建: {args['filepath']}")
                    result = write_file(args['filepath'], args['content'])
                    print(f"   📤 结果: {result}")

                # 将工具执行结果回传给 AI
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": result
                })
        else:
            # AI 没有调用工具，说明它认为任务结束了
            print(f"\n🎉 AI 汇报:\n{msg.content}")
            break


# ==========================================
# 5. 测试运行
# ==========================================
if __name__ == "__main__":
    # 你可以修改这里的指令，测试它的能力
    prompt = input("请输入你想让AI完成的任务: ")
    chat_with_local_agent(prompt)