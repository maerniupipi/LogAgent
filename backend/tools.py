"""自定义工具集"""
from langchain.tools import tool
from datetime import datetime
import json

@tool
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculator(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 数学表达式，例如 "2 + 2" 或 "10 * 5"
    """
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def search_knowledge(query: str) -> str:
    """搜索知识库（示例工具）
    
    Args:
        query: 搜索查询
    """
    # 这里可以连接你的知识库或数据库
    knowledge_base = {
        "python": "Python 是一种高级编程语言",
        "ai": "人工智能是计算机科学的一个分支",
        "dgx": "NVIDIA DGX 是专为 AI 工作负载设计的系统"
    }
    
    for key, value in knowledge_base.items():
        if key in query.lower():
            return value
    
    return "未找到相关信息"

# 工具列表
TOOLS = [get_current_time, calculator, search_knowledge]
