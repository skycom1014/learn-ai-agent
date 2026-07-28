# demo03：带工具调用的 ReAct Agent

一个最小可运行的 Python ReAct 智能体示例。

- 调用兼容 OpenAI 的模型接口
- 使用 SerpApi 进行网页搜索
- 在 `Thought / Action` 步骤之间循环，直到模型返回 `Finish[...]`

## 工作原理

1. `main.py` 解析命令行参数并构建智能体
2. `client.py` 封装兼容 OpenAI 的 LLM 客户端，并以流式方式输出模型结果
3. `tools.py` 注册工具，并实现基于 SerpApi 的 `search` 工具
4. `agent.py` 运行 ReAct 循环：
   - 收集可用工具
   - 生成提示词
   - 调用 LLM
   - 解析 `Thought / Action`
   - 执行 `search[...]`
   - 当返回 `Finish[...]` 时停止

## 项目结构

```text
.
|-- agent.py        # ReAct 智能体循环
|-- client.py       # 兼容 OpenAI 的 LLM 客户端
|-- main.py         # 命令行入口
|-- prompt.py       # ReAct 提示词模板
|-- tools.py        # 工具注册与 SerpApi 搜索
|-- .env.example    # 环境变量模板
`-- README.md
```

## 运行要求

- Python 3.14+
- 一个兼容 OpenAI 的模型服务
- 一个 SerpApi 账号和 API Key

## 安装

推荐使用 `uv`：

```bash
uv sync
```

如果你更习惯使用 `pip`，也可以手动安装 `pyproject.toml` 中声明的依赖。

## 环境变量

将 `.env.example` 复制为 `.env`，并填写真实值：

```env
LLM_API_KEY="你的模型 API Key"
LLM_MODEL_ID="你的模型名称"
LLM_BASE_URL="你的 OpenAI 兼容接口地址"
SERPAPI_API_KEY="你的 SerpApi API Key"
```

| 变量 | 说明 |
| --- | --- |
| `LLM_API_KEY` | 模型服务的 API Key |
| `LLM_MODEL_ID` | 模型名称 / ID |
| `LLM_BASE_URL` | OpenAI 兼容的接口地址 |
| `LLM_TIMEOUT` | 可选，请求超时时间（秒），默认 `60` |
| `SERPAPI_API_KEY` | SerpApi 的 API Key |

## 运行

```bash
uv run python main.py "今天北京天气怎么样？"
```

可以用 `-s/--steps` 设置最大推理步数：

```bash
uv run python main.py "搜索 DeepSeek 的最新信息" -s 5
```

## 工具

当前注册的工具：

- `search[query]`：使用 SerpApi 搜索网页并返回简要摘要

## ReAct 输出格式

模型必须严格遵循以下格式：

```text
Thought: ...
Action: search[你的查询]
```

当答案已经准备好时：

```text
Thought: ...
Action: Finish[最终答案]
```

## 注意事项

- 如果模型没有遵循格式，智能体会直接停止
- 如果缺少 `SERPAPI_API_KEY`，搜索工具会返回错误信息
- 不要将 `.env` 提交到版本控制
