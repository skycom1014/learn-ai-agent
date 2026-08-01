import argparse

from agent import ReflectionAgent
from client import HelloAgentsLLM


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="运行反思式代码生成智能体")
    parser.add_argument(
        "task",
        nargs="?",
        help="要交给智能体处理的任务描述",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="反思优化的最大轮数，默认 3",
    )
    return parser


def main() -> int:
    """程序入口。"""
    parser = build_parser()
    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        return 1

    try:
        llm_client = HelloAgentsLLM()
        agent = ReflectionAgent(llm_client, max_iterations=args.max_iterations)
        agent.run(args.task)
        return 0
    except ValueError as exc:
        print(exc)
        return 1
    except KeyboardInterrupt:
        print("\n用户取消执行。")
        return 130
    except Exception as exc:
        print(f"发生未预期错误: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
