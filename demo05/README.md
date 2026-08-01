# demo05 - 反思式代码生成智能体

这是一个基于大模型的命令行示例项目：

- 先根据任务生成初始代码
- 再对代码进行反思审查
- 最后根据反馈持续优化，直到达到迭代上限或评审认为无需改进

## 功能

- 支持命令行传入任务描述
- 支持配置最大反思轮数
- 通过环境变量配置模型与接口地址
- 使用流式输出实时展示大模型响应

## 项目结构

- `main.py`：程序入口
- `client.py`：OpenAI 兼容客户端封装
- `agent.py`：反思式智能体主流程
- `memory.py`：记录执行与反思轨迹
- `prompt.py`：提示词模板

## 环境要求

- Python 3.10+
- 可用的 OpenAI 兼容接口

## 配置

在项目根目录创建 `.env` 文件，并填写：

```env
LLM_MODEL_ID=你的模型名称
LLM_API_KEY=你的API密钥
LLM_BASE_URL=你的接口地址
LLM_TIMEOUT=60
```

## 安装依赖

```bash
pip install openai python-dotenv
```

## 使用方法

### 直接运行

```bash
python main.py "写一个快速排序函数"
```

### 指定反思轮数

```bash
python main.py "写一个快速排序函数" --max-iterations 5
```

## 工作流程

1. `main.py` 解析命令行参数
2. `HelloAgentsLLM` 初始化 OpenAI 兼容客户端
3. `ReflectionAgent` 根据任务生成初始代码
4. `Memory` 保存每轮代码与反馈
5. `ReflectionAgent` 根据反思结果继续优化

## 示例

```bash
python main.py "实现一个支持缓存的斐波那契函数"
```

## 说明

如果环境变量缺失，程序会提示配置错误并退出。

## 许可

可按你的项目需要补充许可证信息。
