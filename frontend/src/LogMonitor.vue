<template>
  <div class="log-monitor">
    <div class="header">
      <h1>📊 日志监控系统</h1>
      <button @click="showCollectDialog = true" class="btn-primary">采集日志</button>
    </div>

    <!-- 采集对话框 -->
    <div v-if="showCollectDialog" class="modal">
      <div class="modal-content">
        <h2>采集Docker日志</h2>
        <form @submit.prevent="collectLogs">
          <div class="form-group">
            <label>服务器地址</label>
            <input v-model="collectForm.host" required placeholder="192.168.1.100" />
          </div>
          <div class="form-group">
            <label>端口</label>
            <input v-model.number="collectForm.port" type="number" required />
          </div>
          <div class="form-group">
            <label>用户名</label>
            <input v-model="collectForm.username" required />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="collectForm.password" type="password" />
          </div>
          <div class="form-group">
            <label>容器名称</label>
            <input v-model="collectForm.container" required placeholder="otc-market" />
          </div>
          <div class="form-group">
            <label>日志行数</label>
            <input v-model.number="collectForm.lines" type="number" required />
          </div>
          <div class="form-group">
            <label>
              <input v-model="collectForm.analyze" type="checkbox" />
              使用AI分析
            </label>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="collecting">
              {{ collecting ? '采集中...' : '开始采集' }}
            </button>
            <button type="button" @click="showCollectDialog = false" class="btn-secondary">
              取消
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">{{ errors.length }}</div>
        <div class="stat-label">错误总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ newErrorCount }}</div>
        <div class="stat-label">未处理</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ analyzedCount }}</div>
        <div class="stat-label">已分析</div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filters">
      <select v-model="filterStatus" @change="loadErrors">
        <option value="">全部状态</option>
        <option value="new">未处理</option>
        <option value="analyzing">分析中</option>
        <option value="resolved">已解决</option>
      </select>
      <button @click="loadErrors" class="btn-secondary">刷新</button>
    </div>

    <!-- 错误列表 -->
    <div class="error-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="errors.length === 0" class="empty">暂无错误日志</div>
      <div v-else>
        <div 
          v-for="error in errors" 
          :key="error.id" 
          class="error-item"
          @click="selectError(error)"
        >
          <div class="error-header">
            <span class="container-name">{{ error.container_name }}</span>
            <span class="timestamp">{{ formatTime(error.timestamp || error.created_at) }}</span>
            <span :class="['status', error.status]">{{ statusText(error.status) }}</span>
          </div>
          <div class="error-content">{{ error.error_content }}</div>
        </div>
      </div>
    </div>

    <!-- 错误详情 -->
    <div v-if="selectedError" class="modal">
      <div class="modal-content large">
        <h2>错误详情</h2>
        <div class="error-detail">
          <div class="detail-section">
            <h3>基本信息</h3>
            <p><strong>容器:</strong> {{ selectedError.container_name }}</p>
            <p><strong>时间:</strong> {{ selectedError.timestamp }}</p>
            <p><strong>行号:</strong> {{ selectedError.line_number }}</p>
          </div>
          
          <div class="detail-section">
            <h3>错误内容</h3>
            <pre>{{ selectedError.error_content }}</pre>
          </div>
          
          <div v-if="selectedError.context && selectedError.context.length" class="detail-section">
            <h3>上下文</h3>
            <pre>{{ selectedError.context.join('\n') }}</pre>
          </div>
          
          <div v-if="selectedError.analysis" class="detail-section">
            <h3>AI 分析</h3>
            <div class="analysis">{{ selectedError.analysis }}</div>
          </div>
          
          <div class="detail-section">
            <h3>状态管理</h3>
            <select v-model="selectedError.status" @change="updateStatus">
              <option value="new">未处理</option>
              <option value="analyzing">分析中</option>
              <option value="resolved">已解决</option>
              <option value="ignored">忽略</option>
            </select>
          </div>
        </div>
        
        <div class="form-actions">
          <button @click="selectedError = null" class="btn-secondary">关闭</button>
        </div>
      </div>
    </div>
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
      collectForm: {
        host: '',
        port: 22,
        username: '',
        password: '',
        container: 'otc-market',
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
  },
  methods: {
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
      this.collecting = true
      try {
        const response = await fetch('http://localhost:8000/api/collect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ssh_config: {
              host: this.collectForm.host,
              port: this.collectForm.port,
              username: this.collectForm.username,
              password: this.collectForm.password
            },
            container_name: this.collectForm.container,
            lines: this.collectForm.lines,
            analyze: this.collectForm.analyze
          })
        })
        
        const data = await response.json()
        alert(data.message)
        this.showCollectDialog = false
        
        // 等待一下再刷新，让后台分析有时间
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
        console.log('Response text:', text)
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
.log-monitor {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  color: #7f8c8d;
  margin-top: 8px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.error-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  min-height: 400px;
}

.error-item {
  padding: 15px;
  border-bottom: 1px solid #ecf0f1;
  cursor: pointer;
  transition: background 0.2s;
}

.error-item:hover {
  background: #f8f9fa;
}

.error-header {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 8px;
}

.container-name {
  font-weight: bold;
  color: #3498db;
}

.timestamp {
  color: #7f8c8d;
  font-size: 14px;
}

.status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status.new {
  background: #e74c3c;
  color: white;
}

.status.resolved {
  background: #2ecc71;
  color: white;
}

.error-content {
  font-family: monospace;
  font-size: 13px;
  color: #e74c3c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 900px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.detail-section pre {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
}

.analysis {
  background: #e8f5e9;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #4caf50;
  white-space: pre-wrap;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}
</style>
