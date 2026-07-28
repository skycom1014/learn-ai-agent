import re

from client import HelloAgentsLLM
from prompt import REACT_PROMPT_TEMPLATE
from tools import ToolExecutor


class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """运行 ReAct 智能体来回答一个问题。"""
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str,
            )

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("错误: LLM 未能返回有效响应。")
                break

            thought, action = self._parse_output(response_text)

            if thought:
                print(f"思考: {thought}")

            if not action:
                print("警告: 未能解析出有效的 Action，流程终止。")
                break

            final_answer = self._parse_finish_action(action)
            if final_answer is not None:
                print(f"最终答案: {final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if tool_name is None or tool_input is None:
                print(f"警告: 无法解析 Action: {action}")
                break

            print(f"行动: {tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误: 未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input)

            print(f"观察: {observation}")

            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        """解析 LLM 输出，提取 Thought 和 Action。"""
        thought_match = re.search(r"Thought:\s*(.*?)(?=\r?\nAction:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(.+)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_finish_action(self, action_text: str):
        """解析 Finish[...] 指令，允许多行内容。"""
        match = re.fullmatch(r"Finish\[(.*)\]", action_text.strip(), re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _parse_action(self, action_text: str):
        """解析 Tool[input] 格式的 Action。"""
        match = re.fullmatch(r"(\w+)\[(.*)\]", action_text.strip(), re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None
