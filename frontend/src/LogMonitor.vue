<template>
  <div class="log-monitor-wrapper">
    <div class="log-monitor">
      <div class="header">
        <div class="header-content">
          <div class="title-section">
            <div class="icon">📊</div>
            <h1>日志监控</h1>
          </div>
          <button @click="showCollectDialog = true" class="btn-primary">
            <span class="btn-icon">+</span>
            采集日志
          </button>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon error">⚠️</div>
          <div class="stat-info">
            <div class="stat-value">{{ errors.length }}</div>
            <div class="stat-label">错误总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon new">🔴</div>
          <div class="stat-info">
            <div class="stat-value">{{ newErrorCount }}</div>
            <div class="stat-label">未处理</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon success">✓</div>
          <div class="stat-info">
            <div class="stat-value">{{ analyzedCount }}</div>
            <div class="stat-label">已分析</div>
          </div>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="filters">
        <select v-model="filterStatus" @change="loadErrors" class="filter-select">
          <option value="">全部状态</option>
          <option value="new">未处理</option>
          <option value="analyzing">分析中</option>
          <option value="resolved">已解决</option>
        </select>
        <button @click="loadErrors" class="btn-refresh">
          <span class="refresh-icon">↻</span>
        </button>
      </div>

      <!-- 错误列表 -->
      <div class="error-list-container">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        <div v-else-if="errors.length === 0" class="empty-state">
          <div class="empty-icon">✨</div>
          <p>暂无错误日志</p>
        </div>
        <div v-else class="error-list">
          <div 
            v-for="error in errors" 
            :key="error.id" 
            class="error-item"
            @click="selectError(error)"
          >
            <div class="error-header">
              <span class="container-badge">{{ error.container_name }}</span>
              <span :class="['status-badge', error.status]">
                {{ statusText(error.status) }}
              </span>
            </div>
            <div class="error-content">{{ error.error_content }}</div>
            <div class="error-footer">
              <span class="timestamp">{{ formatTime(error.timestamp || error.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 采集对话框 -->
    <transition name="modal">
      <div v-if="showCollectDialog" class="modal-overlay" @click.self="showCollectDialog = false">
        <div class="modal-content">
          <div class="modal-header">
            <h2>采集 Docker 日志</h2>
            <button @click="showCollectDialog = false" class="close-btn">×</button>
          </div>
          <form @submit.prevent="collectLogs" class="modal-form">
            <div class="form-group">
              <label>选择环境</label>
              <select v-model="selectedConfigId" @change="onConfigChange" required>
                <option value="">-- 请选择环境 --</option>
                <option v-for="config in serverConfigs" :key="config.id" :value="config.id">
                  {{ config.name }} ({{ config.host }})
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>服务名称</label>
              <select v-model="collectForm.service" required>
                <option value="">{{ selectedConfigId ? '-- 请选择服务 --' : '-- 请先选择环境 --' }}</option>
                <option v-for="service in availableServices" :key="service" :value="service">
                  {{ service }} (otc-{{ service }})
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>日志行数</label>
              <input v-model.number="collectForm.lines" type="number" required />
            </div>
            <div class="form-group checkbox">
              <label>
                <input v-model="collectForm.analyze" type="checkbox" />
                <span>使用 AI 分析</span>
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="showCollectDialog = false" class="btn-secondary">
                取消
              </button>
              <button type="submit" class="btn-primary" :disabled="collecting || !selectedConfigId || !collectForm.service">
                {{ collecting ? '采集中...' : '开始采集' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>

    <!-- 错误详情 -->
    <transition name="modal">
      <div v-if="selectedError" class="modal-overlay" @click.self="selectedError = null">
        <div class="modal-content large">
          <div class="modal-header">
            <h2>错误详情</h2>
            <button @click="selectedError = null" class="close-btn">×</button>
          </div>
          <div class="error-detail">
            <div class="detail-section">
              <h3>基本信息</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">容器</span>
                  <span class="info-value">{{ selectedError.container_name }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">时间</span>
                  <span class="info-value">{{ selectedError.timestamp }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">行号</span>
                  <span class="info-value">{{ selectedError.line_number }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h3>错误内容</h3>
              <pre class="code-block">{{ selectedError.error_content }}</pre>
            </div>
            
            <div v-if="selectedError.context && selectedError.context.length" class="detail-section">
              <h3>上下文</h3>
              <pre class="code-block">{{ selectedError.context.join('\n') }}</pre>
            </div>
            
            <div v-if="selectedError.analysis" class="detail-section">
              <h3>AI 分析</h3>
              <div class="analysis-box">{{ selectedError.analysis }}</div>
            </div>
            
            <div class="detail-section">
              <h3>状态管理</h3>
              <select v-model="selectedError.status" @change="updateStatus" class="status-select">
                <option value="new">未处理</option>
                <option value="analyzing">分析中</option>
                <option value="resolved">已解决</option>
                <option value="ignored">忽略</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'LogMonitor',
  data() {
    return {
      errors: [],
      selectedError: null,
      loading: false,
      collecting: false,
      showCollectDialog: false,
      filterStatus: '',
      serverConfigs: [],
      selectedConfigId: '',
      availableServices: ['market', 'system', 'infra', 'cgsi', 'gateway', 'bpm', 'trade', 'reference', 'settle', 'capital', 'pricing', 'report'],
      collectForm: {
        service: '',
        lines: 1000,
        analyze: true
      }
    }
  },
  computed: {
    newErrorCount() {
      return this.errors.filter(e => e.status === 'new').length
    },
    analyzedCount() {
      return this.errors.filter(e => e.analysis).length
    }
  },
  mounted() {
    this.loadErrors()
    this.loadConfigs()
  },
  methods: {
    async loadConfigs() {
      try {
        const response = await fetch('http://localhost:8000/api/configs')
        const data = await response.json()
        if (data.success) {
          this.serverConfigs = data.data
        }
      } catch (error) {
        console.error('加载配置失败:', error)
      }
    },
    onConfigChange() {
      // 选择配置后重置服务选择
      this.collectForm.service = ''
    },
    async loadErrors() {
      this.loading = true
      try {
        const params = new URLSearchParams()
        if (this.filterStatus) params.append('status', this.filterStatus)
        
        const response = await fetch(`http://localhost:8000/api/errors?${params}`)
        const data = await response.json()
        this.errors = data.data
      } catch (error) {
        alert('加载失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    async collectLogs() {
      if (!this.selectedConfigId || !this.collectForm.service) {
        alert('请选择环境和服务')
        return
      }
      
      // 拼接容器名称
      const containerName = `otc-${this.collectForm.service}`
      
      this.collecting = true
      try {
        const response = await fetch('http://localhost:8000/api/collect-by-config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            config_id: parseInt(this.selectedConfigId),
            container_name: containerName,
            lines: this.collectForm.lines,
            analyze: this.collectForm.analyze
          })
        })
        
        const data = await response.json()
        alert(data.message || '采集完成')
        this.showCollectDialog = false
        
        // 重置表单
        this.selectedConfigId = ''
        this.collectForm.service = ''
        
        setTimeout(() => this.loadErrors(), 2000)
      } catch (error) {
        alert('采集失败: ' + error.message)
      } finally {
        this.collecting = false
      }
    },
    async selectError(error) {
      try {
        const response = await fetch(`http://localhost:8000/api/errors/${error.id}`)
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        const text = await response.text()
        const data = JSON.parse(text)
        this.selectedError = data.data
      } catch (error) {
        console.error('加载详情失败:', error)
        alert('加载详情失败: ' + error.message)
      }
    },
    async updateStatus() {
      try {
        await fetch(`http://localhost:8000/api/errors/${this.selectedError.id}/status`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: this.selectedError.status })
        })
        this.loadErrors()
      } catch (error) {
        alert('更新失败: ' + error.message)
      }
    },
    formatTime(time) {
      if (!time) return '-'
      return new Date(time).toLocaleString('zh-CN')
    },
    statusText(status) {
      const map = {
        'new': '未处理',
        'analyzing': '分析中',
        'resolved': '已解决',
        'ignored': '已忽略'
      }
      return map[status] || status
    }
  }
}
</script>

<style scoped>
.log-monitor-wrapper {
  width: 100%;
  max-width: 1400px;
  min-width: 1000px;
  padding: 20px;
  margin: 0 auto;
}

.log-monitor {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 28px;
  padding: 28px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.header {
  margin-bottom: 28px;
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
  font-size: 32px;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
}

.header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: rgba(0, 122, 255, 0.9);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: rgba(0, 122, 255, 1);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 122, 255, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 20px;
  font-weight: 300;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 18px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.error {
  background: rgba(255, 59, 48, 0.1);
}

.stat-icon.new {
  background: rgba(255, 149, 0, 0.1);
}

.stat-icon.success {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1d1d1f;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #86868b;
  font-weight: 500;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.filter-select {
  flex: 1;
  max-width: 200px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 12px;
  font-size: 14px;
  color: #1d1d1f;
  cursor: pointer;
  outline: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.btn-refresh {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.btn-refresh:hover {
  transform: rotate(90deg);
}

.refresh-icon {
  font-size: 20px;
  color: #007aff;
}

.error-list-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 18px;
  min-height: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #86868b;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 122, 255, 0.2);
  border-top-color: #007aff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.error-list {
  padding: 12px;
}

.error-item {
  padding: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: background 0.2s ease;
  border-radius: 12px;
  margin-bottom: 8px;
}

.error-item:hover {
  background: rgba(0, 122, 255, 0.05);
}

.error-item:last-child {
  border-bottom: none;
}

.error-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.container-badge {
  padding: 4px 12px;
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.new {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.status-badge.resolved {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.status-badge.analyzing {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.error-content {
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #ff3b30;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 8px;
}

.error-footer {
  display: flex;
  justify-content: flex-end;
}

.timestamp {
  font-size: 12px;
  color: #86868b;
}

/* Modal 样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-content.large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  font-size: 24px;
  color: #86868b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.modal-form {
  padding: 24px 28px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-row .form-group.small {
  grid-column: span 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s ease;
}

.form-group input:focus, .form-group select:focus {
  border-color: #007aff;
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-group.checkbox input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-secondary {
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.05);
  color: #1d1d1f;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.1);
}

.error-detail {
  padding: 24px 28px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #86868b;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 500;
}

.code-block {
  background: #f5f5f7;
  padding: 16px;
  border-radius: 12px;
  overflow-x: auto;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #1d1d1f;
}

.analysis-box {
  background: rgba(52, 199, 89, 0.1);
  padding: 16px;
  border-radius: 12px;
  border-left: 3px solid #34c759;
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.6;
  color: #1d1d1f;
}

.status-select {
  padding: 10px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
}

/* Modal 动画 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content {
  transform: scale(0.9) translateY(20px);
}

.modal-leave-to .modal-content {
  transform: scale(0.9) translateY(20px);
}

@media (max-width: 1024px) {
  .log-monitor-wrapper {
    min-width: 800px;
  }
}

@media (max-width: 768px) {
  .log-monitor-wrapper {
    min-width: auto;
    padding: 10px;
  }
  
  .log-monitor {
    padding: 20px;
    border-radius: 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
