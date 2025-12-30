<template>
  <div id="app">
    <div class="nav-bar" v-if="currentView !== 'home'">
      <button @click="currentView = 'home'" class="back-btn">← 返回首页</button>
    </div>
    
    <Home v-if="currentView === 'home'" @navigate="navigateTo" />
    <ChatApp v-else-if="currentView === 'chat'" />
    <LogMonitor v-else-if="currentView === 'logs'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Home from './Home.vue'
import ChatApp from './ChatApp.vue'
import LogMonitor from './LogMonitor.vue'

const currentView = ref('home')

const navigateTo = (view) => {
  currentView.value = view
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  padding: 15px 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.back-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #5568d3;
}
</style>

<template v-if="false">
  <div class="chat-container">
    <div class="chat-header">
      <h1>🤖 LangGraph Agent</h1>
      <div class="status" :class="{ connected: isConnected }">
        {{ isConnected ? '已连接' : '未连接' }}
      </div>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(msg, index) in messages" :key="index" 
           :class="['message', msg.role]">
        <div class="message-content">
          <div class="message-text">{{ msg.content }}</div>
          <div v-if="msg.tools && msg.tools.length" class="tools-used">
            🔧 使用工具: {{ msg.tools.join(', ') }}
          </div>
        </div>
      </div>
      
      <div v-if="isLoading" class="message assistant">
        <div class="message-content">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <input 
        v-model="userInput" 
        @keyup.enter="sendMessage"
        placeholder="输入消息..."
        :disabled="isLoading"
      />
      <button @click="sendMessage" :disabled="isLoading || !userInput.trim()">
        {{ isLoading ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const isConnected = ref(false)
const messagesContainer = ref(null)
const ws = ref(null)

const API_BASE = 'http://localhost:8080'
const useWebSocket = false // 切换为 true 使用 WebSocket

onMounted(async () => {
  await checkConnection()
  if (useWebSocket) {
    connectWebSocket()
  }
})

const checkConnection = async () => {
  try {
    await axios.get(`${API_BASE}/health`)
    isConnected.value = true
  } catch (error) {
    isConnected.value = false
    console.error('连接失败:', error)
  }
}

const connectWebSocket = () => {
  ws.value = new WebSocket('ws://localhost:8080/ws/chat')
  
  ws.value.onopen = () => {
    isConnected.value = true
    console.log('WebSocket 连接成功')
  }
  
  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    handleWebSocketMessage(data)
  }
  
  ws.value.onerror = () => {
    isConnected.value = false
  }
  
  ws.value.onclose = () => {
    isConnected.value = false
  }
}

const handleWebSocketMessage = (data) => {
  if (data.type === 'message') {
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.complete) {
      lastMsg.content += data.content
    } else {
      messages.value.push({
        role: 'assistant',
        content: data.content,
        complete: false
      })
    }
  } else if (data.type === 'tool_call') {
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg) {
      lastMsg.tools = data.tools
    }
  } else if (data.type === 'end') {
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg) {
      lastMsg.complete = true
    }
    isLoading.value = false
  }
  scrollToBottom()
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return
  
  const message = userInput.value.trim()
  userInput.value = ''
  
  messages.value.push({
    role: 'user',
    content: message
  })
  
  isLoading.value = true
  scrollToBottom()
  
  if (useWebSocket && ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({ message }))
  } else {
    await sendMessageHTTP(message)
  }
}

const sendMessageHTTP = async (message) => {
  try {
    const response = await axios.post(`${API_BASE}/chat`, {
      message: message,
      history: messages.value.slice(0, -1)
    })
    
    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      tools: response.data.tool_calls
    })
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误: ' + error.message
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-container {
  width: 90%;
  max-width: 800px;
  height: 80vh;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.status {
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 14px;
}

.status.connected {
  background: rgba(76, 175, 80, 0.8);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f5f5;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message.assistant .message-content {
  background: white;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-text {
  line-height: 1.5;
}

.tools-used {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
  color: #666;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.chat-input {
  padding: 20px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.chat-input input:focus {
  border-color: #667eea;
}

.chat-input button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.3s;
}

.chat-input button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
</template>

<script v-if="false">
// 旧的聊天组件代码保留在 ChatApp.vue
