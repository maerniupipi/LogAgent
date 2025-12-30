"""直接对接 Qwen 模型 API 的 Agent"""
import requests
from typing import Dict, Any, AsyncIterator
from langchain.tools import tool
from datetime import datetime

# 导入工具
from tools import TOOLS

class QwenAgent:
    """直接调用 Qwen API 的 Agent"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.tools_map = {tool.name: tool for tool in TOOLS}
    
    def _call_qwen_api(self, prompt: str, max_tokens: int = 200) -> Dict[str, Any]:
        """调用 Qwen API"""
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API 返回错误: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"连接失败: {str(e)}"
            }
    
    def _detect_tool_usage(self, user_input: str) -> tuple:
        """检测是否需要使用工具"""
        user_input_lower = user_input.lower()
        
        # 时间相关
        if any(keyword in user_input for keyword in ["时间", "几点", "现在"]):
            return ("get_current_time", {})
        
        # 计算相关
        if any(op in user_input for op in ['+', '-', '*', '/', '×', '÷', '计算']):
            # 提取表达式
            import re
            # 简单提取数字和运算符
            expr = re.sub(r'[^0-9+\-*/×÷().\s]', '', user_input)
            expr = expr.replace('×', '*').replace('÷', '/')
            if expr.strip():
                return ("calculator", {"expression": expr.strip()})
        
        # 知识搜索
        if any(keyword in user_input for keyword in ["什么是", "介绍", "dgx", "python", "ai"]):
            return ("search_knowledge", {"query": user_input})
        
        return (None, None)
    
    def run_sync(self, user_input: str) -> Dict[str, Any]:
        """同步运行"""
        tool_calls = []
        
        # 检测是否需要工具
        tool_name, tool_args = self._detect_tool_usage(user_input)
        
        # 构建提示词
        if tool_name and tool_name in self.tools_map:
            # 先执行工具
            tool = self.tools_map[tool_name]
            try:
                tool_result = tool.invoke(tool_args)
                tool_calls.append(tool_name)
                
                # 将工具结果加入提示词
                prompt = f"""用户问题: {user_input}

工具 {tool_name} 返回结果: {tool_result}

请根据工具结果回答用户的问题。"""
            except Exception as e:
                prompt = f"""用户问题: {user_input}

工具执行失败: {str(e)}

请直接回答用户的问题。"""
        else:
            prompt = user_input
        
        # 调用 Qwen API
        result = self._call_qwen_api(prompt, max_tokens=200)
        
        if result.get("success"):
            return {
                "response": result.get("response", ""),
                "tool_calls": tool_calls
            }
        else:
            return {
                "response": f"错误: {result.get('error', '未知错误')}",
                "tool_calls": []
            }
    
    async def run_stream(self, user_input: str) -> AsyncIterator[dict]:
        """流式运行"""
        result = self.run_sync(user_input)
        
        if result["tool_calls"]:
            yield {
                "type": "tool_call",
                "tools": result["tool_calls"]
            }
        
        yield {
            "type": "message",
            "content": result["response"]
        }
