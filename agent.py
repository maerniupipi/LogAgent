"""LangGraph Agent 实现"""
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from config import LOCAL_MODEL_CONFIG
from tools import TOOLS

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class SimpleAgent:
    def __init__(self):
        # 初始化本地模型
        self.llm = ChatOpenAI(
            base_url=LOCAL_MODEL_CONFIG["base_url"],
            api_key=LOCAL_MODEL_CONFIG["api_key"],
            model=LOCAL_MODEL_CONFIG["model_name"],
            temperature=LOCAL_MODEL_CONFIG["temperature"],
            max_tokens=LOCAL_MODEL_CONFIG["max_tokens"],
        )
        
        # 绑定工具
        self.llm_with_tools = self.llm.bind_tools(TOOLS)
        
        # 创建工具节点
        self.tool_node = ToolNode(TOOLS)
        
        # 构建图
        self.graph = self._build_graph()
    
    def _should_continue(self, state: AgentState):
        """判断是否继续执行工具"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # 如果没有工具调用，结束
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        return "continue"
    
    def _call_model(self, state: AgentState):
        """调用模型"""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _build_graph(self):
        """构建 LangGraph"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self.tool_node)
        
        # 设置入口
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        
        # 工具执行后返回 agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def run(self, user_input: str):
        """运行 agent"""
        initial_state = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        print(f"\n用户: {user_input}")
        print("-" * 50)
        
        # 执行图
        for output in self.graph.stream(initial_state):
            for key, value in output.items():
                if key == "agent":
                    last_msg = value["messages"][-1]
                    if hasattr(last_msg, "content") and last_msg.content:
                        print(f"\nAgent: {last_msg.content}")
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        print(f"\n调用工具: {[tc['name'] for tc in last_msg.tool_calls]}")
                elif key == "tools":
                    tool_msgs = value["messages"]
                    for msg in tool_msgs:
                        if isinstance(msg, ToolMessage):
                            print(f"工具结果: {msg.content}")
        
        print("-" * 50)
