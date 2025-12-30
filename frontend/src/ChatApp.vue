<template>
  <div class="chat-wrapper">
    <div class="chat-container">
      <div class="chat-header">
        <div class="header-content">
          <div class="title-section">
            <div class="icon">💬</div>
            <h1>AI 助手</h1>
          </div>
          <div class="status-badge" :class="{ connected: isConnected }">
            <span class="status-dot"></span>
            {{ isConnected ? '在线' : '离线' }}
          </div>
        </div>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">👋</div>
          <p>你好！我是 AI 助手</p>
          <p class="empty-hint">有什么可以帮你的吗？</p>
        </div>
        
        <div v-for="(msg, index) in messages" :key="index" 
             :class="['message', msg.role]">
          <div class="message-bubble">
            <div class="message-text">{{ msg.content }}</div>
            <div v-if="msg.tools && msg.tools.length" class="tools-badge">
              <span class="tool-icon">🔧</span>
              {{ msg.tools.join(', ') }}
            </div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message assistant">
          <div class="message-bubble">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-wrapper">
        <div class="chat-input">
          <input 
            v-model="userInput" 
            @keyup.enter="sendMessage"
            placeholder="输入消息..."
            :disabled="isLoading"
          />
          <button 
            @click="sendMessage" 
            :disabled="isLoading || !userInput.trim()"
            class="send-button"
          >
            <span v-if="!isLoading">↑</span>
            <span v-else class="loading-spinner"></span>
          </button>
        </div>
      </div>
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
const useWebSocket = false

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
.chat-wrapper {
  width: 100%;
  max-width: 900px;
  min-width: 700px;
  height: 85vh;
  padding: 20px;
}

.chat-container {
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 28px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.chat-header {
  background: rgba(248, 248, 248, 0.95);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 20px 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
}

.chat-header h1 {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.05);
  font-size: 13px;
  font-weight: 500;
  color: #86868b;
  transition: all 0.3s ease;
}

.status-badge.connected {
  background: rgba(52, 199, 89, 0.15);
  color: #34c759;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
}

.status-badge.connected .status-dot {
  background: #34c759;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #1d1d1f;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1));
}

.empty-state p {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 15px !important;
  opacity: 0.7;
  font-weight: 400 !important;
}

.message {
  margin-bottom: 16px;
  display: flex;
  animation: messageSlide 0.3s ease-out;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: 20px;
  word-wrap: break-word;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.message.user .message-bubble {
  background: rgba(0, 122, 255, 0.9);
  color: white;
  border-bottom-right-radius: 6px;
}

.message.assistant .message-bubble {
  background: rgba(255, 255, 255, 0.95);
  color: #1d1d1f;
  border-bottom-left-radius: 6px;
}

.message-text {
  line-height: 1.5;
  font-size: 15px;
}

.tools-badge {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tool-icon {
  font-size: 14px;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 4px 0;
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
    opacity: 0.7;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

.chat-input-wrapper {
  padding: 16px 20px 20px;
  background: rgba(248, 248, 248, 0.95);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.chat-input {
  display: flex;
  gap: 10px;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 8px 8px 8px 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.chat-input input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  color: #1d1d1f;
  outline: none;
  padding: 8px 0;
}

.chat-input input::placeholder {
  color: #86868b;
}

.send-button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: #007aff;
  color: white;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #0051d5;
  transform: scale(1.05);
}

.send-button:active:not(:disabled) {
  transform: scale(0.95);
}

.send-button:disabled {
  background: #c7c7cc;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .chat-wrapper {
    min-width: auto;
    padding: 10px;
    height: 90vh;
  }
  
  .chat-container {
    border-radius: 20px;
  }
  
  .chat-header {
    padding: 16px 20px;
  }
  
  .chat-header h1 {
    font-size: 18px;
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .chat-input-wrapper {
    padding: 12px 16px 16px;
  }
}
</style>
