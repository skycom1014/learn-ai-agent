import argparse
import ast
from typing import Optional

from client import HelloAgentsLLM
from prompt import PLANNER_PROMPT_TEMPLATE, EXECUTOR_PROMPT_TEMPLATE


class Planner:
    def __init__(self, client: HelloAgentsLLM):
        self.llm_client = client

    def plan(self, question: str) -> list[str]:
        """根据用户问题生成一个行动计划。"""
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        # 为了生成计划，我们构建一个简单的消息列表
        messages = [{"role": "user", "content": prompt}]

        print("--- 正在生成计划 ---")
        # 使用流式输出来获取完整的计划
        response_text = self.llm_client.think(messages=messages) or ""

        print(f"✅ 计划已生成:\n{response_text}")

        # 解析 LLM 输出的列表字符串
        try:
            # 找到 ```python 和 ``` 之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # 使用 ast.literal_eval 安全地将字符串转换为 Python 列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []


class Executor:
    def __init__(self, client: HelloAgentsLLM):
        self.llm_client = client

    def execute(self, question: str, plan: list[str]) -> str:
        """根据计划，逐步执行并解决问题。"""
        history = ""  # 用于存储历史步骤和结果的字符串

        print("\n--- 正在执行计划 ---")
        response_text = ""

        for i, step in enumerate(plan, start=1):
            print(f"\n-> 正在执行步骤 {i}/{len(plan)}: {step}")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",  # 如果是第一步，则历史为空
                current_step=step,
            )

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages) or ""

            # 更新历史记录，为下一步做准备
            history += f"步骤 {i}: {step}\n结果: {response_text}\n\n"

            print(f"✅ 步骤 {i} 已完成，结果: {response_text}")

        # 循环结束后，最后一步的响应就是最终答案
        return response_text


class PlanAndSolveAgent:
    def __init__(self, client: HelloAgentsLLM):
        """初始化智能体，同时创建规划器和执行器实例。"""
        self.llm_client = client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str) -> Optional[str]:
        """运行智能体的完整流程：先规划，后执行。"""
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        # 1. 调用规划器生成计划
        plan = self.planner.plan(question)

        # 检查计划是否成功生成
        if not plan:
            print("\n--- 任务终止 ---\n无法生成有效的行动计划。")
            return None

        # 2. 调用执行器执行计划
        final_answer = self.executor.execute(question, plan)

        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
        return final_answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 Plan-and-Solve 智能体")
    parser.add_argument(
        "question",
        nargs="*",
        help="要解决的问题；如果不传则在启动后交互式输入",
    )
    return parser.parse_args()


def get_question_from_args(args: argparse.Namespace) -> str:
    question = " ".join(args.question).strip()
    if question:
        return question
    return input("请输入你的问题：").strip()


def main() -> None:
    args = parse_args()
    question = get_question_from_args(args)

    if not question:
        print("❌ 未提供有效问题，程序结束。")
        return

    try:
        llm_client = HelloAgentsLLM()
        agent = PlanAndSolveAgent(llm_client)
        agent.run(question)
    except ValueError as e:
        print(f"❌ 初始化失败: {e}")
    except KeyboardInterrupt:
        print("\n⚠️ 程序已中断。")


if __name__ == "__main__":
    main()
