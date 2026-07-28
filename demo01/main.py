import re
import os

# --- 0. 加载 .env 文件中的环境变量 ---
def load_env(path=".env"):
    """简易 .env 文件加载器"""
    env_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    if key not in os.environ:  # 不覆盖已设置的环境变量
                        os.environ[key] = value

load_env()

# --- 1. 配置LLM客户端 ---
API_KEY = os.environ.get("API_KEY", "YOUR_API_KEY")
BASE_URL = os.environ.get("BASE_URL", "YOUR_BASE_URL")
MODEL_ID = os.environ.get("MODEL_ID", "YOUR_MODEL_ID")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "YOUR_TAVILY_API_KEY")
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# 校验必要配置
if API_KEY == "YOUR_API_KEY":
    print("❌ 请先配置 .env 文件中的 API_KEY / BASE_URL / MODEL_ID / TAVILY_API_KEY")
    exit(1)

from client import OpenAICompatibleClient
from tools import get_weather, get_attraction, get_user_preferences, update_user_preference, check_ticket_availability

from system_prompt import AGENT_SYSTEM_PROMPT

llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 1.5 注册可用工具 ---
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
    "get_user_preferences": get_user_preferences,
    "update_user_preference": update_user_preference,
    "check_ticket_availability": check_ticket_availability,
}

# --- 2. 初始化 ---
user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

# 拒绝跟踪状态（功能3: 反思）
reject_count = 0
rejected_attractions = []

print(f"用户输入: {user_prompt}\n" + "="*40)

# --- 3. 运行主循环 ---
for i in range(10): # 设置最大循环次数（加大以支持查偏好+验票+备选搜索+反思）
    print(f"--- 循环 {i+1} ---\n")
    
    # 3.1. 构建Prompt（注入用户偏好 — 功能1: 记忆）
    full_prompt = "\n".join(prompt_history)
    profile = get_user_preferences()
    if "暂无" not in profile:
        full_prompt = f"[用户偏好]\n{profile}\n\n{full_prompt}"
    
    # 3.2. 调用LLM进行思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)

    # 空响应恢复：提示模型重新输出
    if not llm_output or not llm_output.strip():
        print("⚠️ 模型返回空响应，注入恢复提示...")
        prompt_history.append("Observation: 错误: 上一条回复为空，请重新输出 Thought 和 Action。")
        continue

    # 模型可能会输出多余的Thought-Action，需要截断
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action 对")
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)
    
    # 3.3. 解析并执行行动
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "="*40)
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    if action_str.startswith("Finish"):
        final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"\n{'='*40}")
        print(f"🤖 Agent 推荐: {final_answer}")
        print(f"{'='*40}")

        # 功能3: 交互式反馈 + 拒绝反思
        feedback = input("\n你满意这个推荐吗？(y=满意 / n=换一个): ").strip().lower()
        if feedback == 'y':
            print("✅ 用户满意，任务完成！")
            break
        else:
            reject_count += 1
            rejected_attractions.append(final_answer[:80])
            print(f"❌ 用户拒绝 (第 {reject_count} 次)")

            if reject_count >= 3:
                reflection = (
                    f"[系统反思] 你已经连续推荐了 {reject_count} 个方案都被用户拒绝了。"
                    f"已拒绝的推荐: {'; '.join(rejected_attractions)}。"
                    f"请认真反思：用户可能对什么不满意？是否需要调整推荐策略？"
                    f"建议：调用 get_user_preferences 查看用户偏好，"
                    f"或换一种类型的景点（如从自然风光改为历史文化），"
                    f"或直接询问用户想要什么类型的景点。"
                )
                prompt_history.append(reflection)
                rejected_attractions = []
                reject_count = 0
                print("⚡ 触发反思机制：Agent 正在重新分析...\n")
            else:
                prompt_history.append(f"用户反馈: 不喜欢这个推荐，请换一个不同的景点。")

            print(f"{'='*40}")
            continue
    
    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误:未定义的工具 '{tool_name}'"

    # 3.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)
