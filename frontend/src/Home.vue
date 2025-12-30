<template>
  <div class="home">
    <div class="welcome-section">
      <h1 class="title">欢迎使用</h1>
      <p class="subtitle">选择一个应用开始</p>
    </div>
    
    <div class="app-grid">
      <div class="app-card" @click="$emit('navigate', 'chat')">
        <div class="card-background"></div>
        <div class="card-content">
          <div class="app-icon">💬</div>
          <h2>AI 聊天助手</h2>
          <p>与智能助手对话交流</p>
          <div class="arrow">→</div>
        </div>
      </div>
      
      <div class="app-card" @click="$emit('navigate', 'logs')">
        <div class="card-background"></div>
        <div class="card-content">
          <div class="app-icon">📊</div>
          <h2>日志监控</h2>
          <p>实时监控系统日志</p>
          <div class="arrow">→</div>
        </div>
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
  width: 100%;
  max-width: 1000px;
  min-width: 800px;
  padding: 60px 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 60px;
  animation: fadeInDown 0.6s ease-out;
}

.title {
  font-size: 56px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 12px;
  letter-spacing: -1.5px;
}

.subtitle {
  font-size: 20px;
  color: #6e6e73;
  font-weight: 400;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.app-card {
  position: relative;
  height: 280px;
  border-radius: 24px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-background {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.app-card:hover .card-background {
  background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0.95) 100%);
  border-color: rgba(0, 0, 0, 0.1);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.app-card:hover {
  transform: translateY(-8px) scale(1.02);
}

.card-content {
  position: relative;
  height: 100%;
  padding: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  z-index: 1;
}

.app-icon {
  font-size: 72px;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1));
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-card:hover .app-icon {
  transform: scale(1.1);
}

.app-card h2 {
  font-size: 26px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.app-card p {
  color: #6e6e73;
  font-size: 15px;
  font-weight: 400;
  line-height: 1.4;
}

.arrow {
  position: absolute;
  bottom: 24px;
  right: 24px;
  font-size: 24px;
  color: #007aff;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-card:hover .arrow {
  opacity: 1;
  transform: translateX(0);
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .home {
    min-width: auto;
    padding: 40px 16px;
  }
  
  .title {
    font-size: 42px;
  }
  
  .subtitle {
    font-size: 18px;
  }
  
  .app-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .app-card {
    height: 240px;
  }
}
</style>
