"""FastAPI 后端服务"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载上级目录的 .env 文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 检查是否使用测试模式
USE_MOCK = os.getenv("USE_MOCK_AGENT", "false").lower() == "true"
MODEL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:8000/v1")

# 提取 base_url（去掉 /v1）
if MODEL_URL.endswith('/v1'):
    BASE_URL = MODEL_URL[:-3]
else:
    BASE_URL = MODEL_URL

if USE_MOCK:
    print("⚠️  使用测试模式 (Mock Agent)")
    from mock_agent import MockAgent
    agent = MockAgent()
else:
    print(f"✅ 使用 Qwen 模型: {BASE_URL}")
    from qwen_agent import QwenAgent
    agent = QwenAgent(base_url=BASE_URL)

app = FastAPI(title="LangGraph Agent API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[str]] = []

@app.get("/")
async def root():
    return {"message": "LangGraph Agent API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """同步聊天接口"""
    try:
        result = agent.run_sync(request.message)
        return ChatResponse(
            response=result["response"],
            tool_calls=result.get("tool_calls", [])
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"错误详情: {error_detail}")
        return ChatResponse(
            response=f"错误: {str(e)}\n\n详细信息: 请检查模型服务是否运行在 http://172.16.50.103:8000",
            tool_calls=[]
        )

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 流式聊天"""
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            # 发送开始信号
            await websocket.send_json({
                "type": "start",
                "message": "处理中..."
            })
            
            # 流式处理
            async for chunk in agent.run_stream(user_message):
                await websocket.send_json(chunk)
            
            # 发送结束信号
            await websocket.send_json({
                "type": "end",
                "message": "完成"
            })
            
    except WebSocketDisconnect:
        print("WebSocket 连接断开")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
