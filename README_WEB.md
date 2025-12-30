# LangGraph Agent Web 应用

前后端分离的 AI Agent 聊天应用。

## 技术栈

**后端:**
- FastAPI - 高性能 Web 框架
- LangChain + LangGraph - Agent 框架
- WebSocket - 实时通信支持

**前端:**
- Vue 3 - 渐进式框架
- Vite - 快速构建工具
- Axios - HTTP 客户端

## 项目结构

```
.
├── backend/              # 后端服务
│   ├── api.py           # FastAPI 应用
│   ├── agent.py         # Agent 逻辑
│   ├── tools.py         # 工具集
│   └── config.py        # 配置
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── App.vue     # 主组件
│   │   └── main.js     # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── requirements.txt     # Python 依赖
└── .env.example        # 环境变量示例
```

## 快速开始

### 1. 配置环境

```bash
# 复制环境变量文件
copy .env.example .env

# 编辑 .env，设置你的模型地址
```

### 2. 启动后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 启动后端服务（方式1：使用脚本）
start_backend.bat

# 或者手动启动（方式2）
cd backend
python api.py
```

后端将运行在: http://localhost:8080

### 3. 启动前端

```bash
# 安装前端依赖
cd frontend
npm install

# 启动开发服务器（方式1：使用脚本）
cd ..
start_frontend.bat

# 或者手动启动（方式2）
cd frontend
npm run dev
```

前端将运行在: http://localhost:3000

### 4. 访问应用

打开浏览器访问: http://localhost:3000

## API 接口

### REST API

**POST /chat**
```json
{
  "message": "你好",
  "history": []
}
```

响应:
```json
{
  "response": "你好！有什么可以帮助你的吗？",
  "tool_calls": []
}
```

### WebSocket

连接: `ws://localhost:8080/ws/chat`

发送消息:
```json
{
  "message": "现在几点了？"
}
```

接收消息:
```json
{
  "type": "message",
  "content": "当前时间是..."
}
```

## 功能特性

✅ 实时聊天界面
✅ 支持工具调用显示
✅ REST API 和 WebSocket 双模式
✅ 响应式设计
✅ 打字动画效果
✅ 连接状态显示

## 自定义配置

### 切换 WebSocket 模式

在 `frontend/src/App.vue` 中修改:
```javascript
const useWebSocket = true  // 改为 true 启用 WebSocket
```

### 修改端口

**后端:** 在 `backend/api.py` 中修改:
```python
uvicorn.run(app, host="0.0.0.0", port=8080)
```

**前端:** 在 `frontend/vite.config.js` 中修改:
```javascript
server: {
  port: 3000
}
```

## 生产部署

### 后端

```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8080 --workers 4
```

### 前端

```bash
cd frontend
npm run build
# 构建产物在 frontend/dist 目录
```

## 故障排除

**后端无法启动:**
- 检查端口 8080 是否被占用
- 确认已安装所有依赖
- 检查模型服务是否运行

**前端无法连接:**
- 确认后端已启动
- 检查 CORS 配置
- 查看浏览器控制台错误

**工具调用失败:**
- 检查模型是否支持 function calling
- 查看后端日志
