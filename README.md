# LangGraph Agent 项目

基于 LangChain 和 LangGraph 的简单 Agent 系统，连接本地部署的模型。

## 项目结构

```
.
├── requirements.txt    # Python 依赖
├── config.py          # 配置文件
├── agent.py           # Agent 核心逻辑
├── tools.py           # 自定义工具
├── main.py            # 程序入口
├── .env.example       # 环境变量示例
└── README.md          # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

根据你的 DGX 模型部署情况修改：
- `LOCAL_MODEL_URL`: 模型 API 地址
- `LOCAL_MODEL_NAME`: 模型名称

### 3. 运行

```bash
python main.py
```

## 功能特性

- ✅ 连接本地部署的模型
- ✅ 基于 LangGraph 的状态管理
- ✅ 内置多个实用工具
- ✅ 支持工具调用和多轮对话
- ✅ 交互式命令行界面

## 自定义工具

在 `tools.py` 中添加新工具：

```python
@tool
def your_custom_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result
```

## Agent 工作流程

1. 用户输入问题
2. Agent 分析并决定是否需要调用工具
3. 如需工具，执行工具并获取结果
4. Agent 综合信息生成最终回答

## 注意事项

- 确保本地模型服务已启动
- 模型需要支持 OpenAI 兼容的 API 格式
- 可根据需要调整 `config.py` 中的参数
