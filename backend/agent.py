"""LangGraph Agent 实现（后端版本）"""
from typing import TypedDict, Annotated, Sequence, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from config import LOCAL_MODEL_CONFIG
from tools import TOOLS

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class SimpleAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=LOCAL_MODEL_CONFIG["base_url"],
            api_key=LOCAL_MODEL_CONFIG["api_key"],
            model=LOCAL_MODEL_CONFIG["model_name"],
            temperature=LOCAL_MODEL_CONFIG["temperature"],
            max_tokens=LOCAL_MODEL_CONFIG["max_tokens"],
        )
        
        self.llm_with_tools = self.llm.bind_tools(TOOLS)
        self.tool_node = ToolNode(TOOLS)
        self.graph = self._build_graph()
    
    def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        return "continue"
    
    def _call_model(self, state: AgentState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        
        workflow.add_edge("tools", "agent")
        return workflow.compile()
    
    def run_sync(self, user_input: str):
        """同步运行（用于 REST API）"""
        initial_state = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        tool_calls = []
        final_response = ""
        
        for output in self.graph.stream(initial_state):
            for key, value in output.items():
                if key == "agent":
                    last_msg = value["messages"][-1]
                    if hasattr(last_msg, "content") and last_msg.content:
                        final_response = last_msg.content
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        tool_calls.extend([tc['name'] for tc in last_msg.tool_calls])
        
        return {
            "response": final_response,
            "tool_calls": tool_calls
        }
    
    async def run_stream(self, user_input: str) -> AsyncIterator[dict]:
        """流式运行（用于 WebSocket）"""
        initial_state = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        for output in self.graph.stream(initial_state):
            for key, value in output.items():
                if key == "agent":
                    last_msg = value["messages"][-1]
                    
                    if hasattr(last_msg, "content") and last_msg.content:
                        yield {
                            "type": "message",
                            "content": last_msg.content
                        }
                    
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        yield {
                            "type": "tool_call",
                            "tools": [tc['name'] for tc in last_msg.tool_calls]
                        }
                
                elif key == "tools":
                    tool_msgs = value["messages"]
                    for msg in tool_msgs:
                        if isinstance(msg, ToolMessage):
                            yield {
                                "type": "tool_result",
                                "content": msg.content
                            }
