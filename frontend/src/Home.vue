<template>
  <div class="home">
    <h1>🚀 应用中心</h1>
    <div class="app-grid">
      <div class="app-card" @click="$emit('navigate', 'chat')">
        <div class="app-icon">🤖</div>
        <h2>AI 聊天助手</h2>
        <p>与 LangGraph Agent 对话</p>
      </div>
      
      <div class="app-card" @click="$emit('navigate', 'logs')">
        <div class="app-icon">📊</div>
        <h2>日志监控系统</h2>
        <p>自动采集和分析线上日志</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  emits: ['navigate']
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 40px;
}

h1 {
  font-size: 48px;
  margin-bottom: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1000px;
  margin: 0 auto;
}

.app-card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.app-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.app-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.app-card h2 {
  font-size: 24px;
  margin-bottom: 10px;
  color: #2c3e50;
}

.app-card p {
  color: #7f8c8d;
  font-size: 16px;
}
</style>
