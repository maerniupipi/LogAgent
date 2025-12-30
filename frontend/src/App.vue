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
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
  background: linear-gradient(180deg, #f5f5f7 0%, #e8e8ed 100%);
  background-attachment: fixed;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
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
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  padding: 12px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 1px 10px rgba(0, 0, 0, 0.05);
  z-index: 100;
  animation: slideDown 0.4s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(0, 122, 255, 0.15);
  transform: translateX(-2px);
}

.back-btn:active {
  transform: scale(0.96);
}
</style>
