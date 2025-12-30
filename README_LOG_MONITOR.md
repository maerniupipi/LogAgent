# 日志监控系统

自动读取线上环境的Docker容器日志，使用AI解读错误，提供Web界面查看。

## 功能特性

- 🔌 **SSH连接** - 通过SSH连接远程服务器
- 🐳 **Docker日志采集** - 自动执行 `docker logs` 命令
- 🤖 **AI智能分析** - 使用AI解读错误原因和解决方案
- 💾 **数据存储** - SQLite存储解析后的日志
- 🎨 **Web界面** - 友好的界面查看和管理错误日志
- 📊 **统计分析** - 错误数量、状态统计

## 快速开始

### 1. 安装依赖

```bash
pip install paramiko fastapi uvicorn
```

### 2. 启动后端

```bash
# Windows
start_log_monitor.bat

# Linux/Mac
cd backend
python log_api.py
```

后端将运行在 `http://localhost:8000`

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端将运行在 `http://localhost:5173`

## 使用方法

### 采集日志

1. 点击"采集日志"按钮
2. 填写SSH连接信息：
   - 服务器地址
   - 端口（默认22）
   - 用户名
   - 密码
3. 填写容器名称（如：otc-market）
4. 设置要采集的日志行数（默认1000）
5. 勾选"使用AI分析"（推荐）
6. 点击"开始采集"

### 查看错误

- 错误列表显示所有采集到的错误
- 点击错误可查看详情
- 详情包括：
  - 错误内容
  - 上下文（堆栈信息）
  - AI分析结果
  - 状态管理

### 状态管理

- **未处理** - 新采集的错误
- **分析中** - AI正在分析
- **已解决** - 已修复的错误
- **已忽略** - 可忽略的错误

## API接口

### 采集日志
```
POST /api/collect
```

### 获取错误列表
```
GET /api/errors?container_name=xxx&status=new&limit=100
```

### 获取错误详情
```
GET /api/errors/{error_id}
```

### 更新错误状态
```
PUT /api/errors/{error_id}/status
```

### 获取采集历史
```
GET /api/history
```

## 配置说明

### SSH密钥认证

如果使用SSH密钥而不是密码：

```python
{
  "ssh_config": {
    "host": "192.168.1.100",
    "port": 22,
    "username": "root",
    "key_file": "/path/to/private_key"
  }
}
```

### 定时采集

可以使用系统定时任务（cron/Task Scheduler）定期调用API采集日志：

```bash
# Linux cron示例 - 每小时采集一次
0 * * * * curl -X POST http://localhost:8000/api/collect -H "Content-Type: application/json" -d '{"ssh_config":{"host":"xxx","username":"xxx","password":"xxx"},"container_name":"otc-market","lines":1000,"analyze":true}'
```

## 注意事项

1. **安全性** - SSH密码会在内存中传输，建议使用密钥认证
2. **性能** - AI分析在后台异步执行，不会阻塞采集
3. **存储** - 日志存储在 `logs.db` SQLite数据库中
4. **日志量** - 建议根据实际情况调整采集行数，避免过大

## 扩展功能

### 支持多容器

可以配置多个容器的采集任务，系统会分别存储和展示。

### 告警通知

可以扩展添加：
- 邮件通知
- 钉钉/企业微信通知
- Slack通知

### 日志过滤

可以添加关键词过滤，只采集特定类型的错误。

## 故障排查

### SSH连接失败
- 检查服务器地址和端口
- 确认用户名密码正确
- 检查防火墙设置

### Docker命令失败
- 确认容器名称正确
- 确认SSH用户有Docker权限

### AI分析失败
- 检查Qwen Agent配置
- 查看后端日志
