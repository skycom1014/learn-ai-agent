# demo-01

一个基于 **OpenAI 兼容接口** 的 Python 旅行助手 Demo。

它会让大模型按 `Thought -> Action` 的方式工作，并结合外部工具完成以下事情：

- 查询指定城市的实时天气
- 基于天气推荐旅游景点
- 记录并读取用户偏好
- 在推荐前检查门票是否可购
- 支持在多次被拒绝后触发反思并调整推荐策略

## 项目特点

- 使用 `openai` SDK 调用兼容 OpenAI Chat Completions 的模型服务
- 通过 `wttr.in` 获取天气数据
- 通过 `tavily-python` 做景点搜索
- 通过内存变量模拟用户画像与门票库存
- 使用固定系统提示词约束模型输出格式

## 目录说明

- `main.py`：主程序，负责加载环境变量、循环调用模型、解析 Action 并执行工具
- `client.py`：OpenAI 兼容客户端封装
- `tools.py`：天气、景点、偏好、门票相关工具
- `system_prompt.py`：智能旅行助手的系统提示词
- `.env.example`：环境变量示例
- `pyproject.toml`：项目依赖与 Python 版本配置

## 运行环境

- Python `3.14`

## 安装依赖

建议使用 `uv`：

```bash
uv sync
```

如果你使用的是其他虚拟环境工具，也可以按 `pyproject.toml` 中的依赖自行安装。

## 配置

先复制环境变量示例文件并填写真实值：

```bash
cp .env.example .env
```

需要配置的变量：

- `API_KEY`：OpenAI 兼容服务的 API Key
- `BASE_URL`：OpenAI 兼容服务的 Base URL
- `MODEL_ID`：模型名称或 ID
- `TAVILY_API_KEY`：Tavily 搜索接口密钥

## 运行

直接执行主程序：

```bash
python main.py
```

程序默认会询问一个示例问题：

> 你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。

你可以在运行过程中对推荐结果进行反馈：

- 输入 `y`：接受当前推荐
- 输入 `n`：拒绝并让系统继续推荐其他景点

## 工作流程

主流程大致如下：

1. 读取用户偏好
2. 将用户请求与历史上下文拼成提示词
3. 调用大模型生成 `Thought` 和 `Action`
4. 解析 `Action` 并执行对应工具
5. 把工具结果作为 `Observation` 写回上下文
6. 继续迭代，直到模型输出 `Finish[...]`

## 工具说明

### `get_weather(city)`
查询指定城市的实时天气。

### `get_attraction(city, weather)`
根据城市和天气检索适合的旅游景点推荐。

### `get_user_preferences()`
读取当前会话中已记录的用户偏好。

### `update_user_preference(key, value)`
记录用户明确表达的偏好。

### `check_ticket_availability(attraction, date)`
模拟检查景点门票是否可购。

## 注意事项

- `tools.py` 里的用户偏好和售罄列表都是内存级别的，程序退出后不会持久化
- `check_ticket_availability` 是 Demo 级模拟逻辑，不是真实票务系统
- 如果 `API_KEY` 没有配置，程序会直接退出
- `wttr.in` 和 Tavily 都依赖外部网络，网络不可用时会返回错误信息

## 示例

你可以把它理解成一个“会查天气、会搜景点、会记偏好”的旅行助手 Demo。

如果想继续扩展，可以考虑：

- 把用户画像持久化到数据库或文件
- 为工具调用增加更严格的结构化解析
- 增加更多城市/景点策略
- 将交互式 CLI 改成 Web UI
