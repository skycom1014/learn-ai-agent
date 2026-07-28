import argparse

from agent import ReActAgent
from client import HelloAgentsLLM
from tools import ToolExecutor, search


def build_agent(max_steps: int = 5) -> ReActAgent:
    """构建并初始化 ReAct 智能体。"""
    llm_client = HelloAgentsLLM()
    tool_executor = ToolExecutor()
    tool_executor.registerTool(
        "search",
        "使用 SerpApi 搜索网页并返回摘要。",
        search,
    )
    return ReActAgent(llm_client=llm_client, tool_executor=tool_executor, max_steps=max_steps)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="启动 demo03 ReAct 智能体")
    parser.add_argument("question", help="要让智能体回答的问题")
    parser.add_argument(
        "-s",
        "--steps",
        type=int,
        default=5,
        help="智能体最大推理步数，默认 5",
    )
    return parser.parse_args()


def main() -> int:
    """项目入口。"""
    args = parse_args()

    try:
        agent = build_agent(max_steps=args.steps)
        answer = agent.run(args.question)
        if answer:
            print()
            print(f"最终答案：{answer}")
            return 0

        print()
        print("未获得最终答案。")
        return 2
    except ValueError as exc:
        print(f"启动失败：{exc}")
        return 1
    except KeyboardInterrupt:
        print()
        print("已取消。")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
