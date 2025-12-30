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
