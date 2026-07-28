# demo04

一个基于 **Plan-and-Solve** 思路的简单智能体示例项目。

程序会先让大模型为用户问题生成一份分步骤计划，再按步骤逐个执行，最终输出答案。

## 项目结构

```text
.
├─ client.py      # LLM 客户端封装，负责读取 .env 并调用 OpenAI 兼容接口
├─ prompt.py      # Planner / Executor 使用的提示词模板
├─ main.py        # 主程序入口，串联规划与执行流程
├─ .env.example   # 环境变量示例
├─ pyproject.toml # 项目依赖配置
└─ README.md
```

## 运行环境

- Python >= 3.14
- 一个可用的 OpenAI 兼容大模型服务

项目当前依赖：

- `openai`
- `python-dotenv`

## 安装依赖

### 方式 1：使用 uv（推荐）

如果你本机已安装 `uv`：

```bash
uv sync
```

### 方式 2：使用 pip

如果你使用普通 `pip`，可手动安装依赖：

```bash
pip install openai python-dotenv
```

## 配置环境变量

先复制一份环境变量模板：

```bash
cp .env.example .env
```

如果你在 Windows PowerShell 中，也可以手动创建 `.env` 文件。

然后填写以下配置：

```env
LLM_API_KEY="YOUR-LLM-API-KEY"
LLM_MODEL_ID="YOUR-MODEL"
LLM_BASE_URL="YOUR-URL"
SERPAPI_API_KEY="YOUR_SERPAPI_API_KEY"
```

### 关键字段说明

- `LLM_API_KEY`：模型服务的 API Key
- `LLM_MODEL_ID`：要调用的模型名称
- `LLM_BASE_URL`：OpenAI 兼容接口地址
- `SERPAPI_API_KEY`：当前示例中**暂未使用**，可以先保留为空或按需填写

此外，`client.py` 还支持可选超时配置：

```env
LLM_TIMEOUT=60
```

未设置时默认超时为 `60` 秒。

## 使用方法

### 方式 1：命令行直接传入问题

```bash
python main.py "请帮我分析快速排序的时间复杂度"
```

### 方式 2：启动后交互式输入

```bash
python main.py
```

运行后会提示：

```text
请输入你的问题：
```

输入问题后，程序会自动执行完整流程。

## 程序执行流程

`main.py` 的主流程如下：

1. 读取命令行参数或交互输入的问题
2. 初始化 `HelloAgentsLLM`
3. 创建 `PlanAndSolveAgent`
4. `Planner` 先生成计划
5. `Executor` 再按计划逐步执行
6. 输出最终答案

## 示例输出

程序运行时会看到类似输出：

```text
--- 开始处理问题 ---
问题: 请帮我分析快速排序的时间复杂度

--- 正在生成计划 ---
...

--- 正在执行计划 ---
-> 正在执行步骤 1/3: ...
-> 正在执行步骤 2/3: ...
-> 正在执行步骤 3/3: ...

--- 任务完成 ---
最终答案: ...
```

## 单独测试 LLM 客户端

如果你只想验证模型连接是否正常，也可以直接运行：

```bash
python client.py
```

它会使用 `client.py` 中内置的示例消息测试一次模型调用。

## 常见问题

### 1. 提示“初始化失败”

通常是以下原因之一：

- `.env` 文件不存在
- `LLM_API_KEY` / `LLM_MODEL_ID` / `LLM_BASE_URL` 未填写完整
- 填写的接口地址不可用

### 2. 无法生成有效的行动计划

这是因为 `Planner` 期望模型严格按如下格式返回：

````text
```python
["步骤1", "步骤2", "步骤3"]
```
````

如果模型输出不符合这个格式，程序就无法成功解析计划。

### 3. 接口响应很慢或超时

可以尝试在 `.env` 中增大：

```env
LLM_TIMEOUT=120
```

## 后续可扩展方向

你可以继续在这个项目上扩展：

- 为 Planner / Executor 增加重试机制
- 将每一步执行结果保存到日志文件
- 增加 Web 搜索、工具调用或记忆模块
- 将最终结果输出为 Markdown 或 JSON

---

如果你刚开始接触这个项目，建议先按下面顺序体验：

1. 配好 `.env`
2. 运行 `python client.py` 测试模型连通性
3. 再运行 `python main.py "你的问题"` 体验完整智能体流程
