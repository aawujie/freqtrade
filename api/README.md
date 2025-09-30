# Freqtrade API

将 Freqtrade 命令封装为 REST API，方便前端调用。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd api
pip3 install -r requirements.txt
```

或使用 uv：
```bash
uv pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方式 1: 使用启动脚本
./start.sh

# 方式 2: 直接运行
python3 main.py

# 方式 3: 使用 uvicorn（推荐生产环境）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问 API

- **API 地址**: http://localhost:8000
- **交互式文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc

---

## 📖 API 端点

### 基础接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | API 信息 |
| GET | `/health` | 健康检查 |
| GET | `/system/info` | 系统信息 |

### 交易控制

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/trade/start` | 启动交易 |
| POST | `/trade/stop` | 停止交易 |
| GET | `/trade/status` | 获取交易状态 |

### 回测

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/backtest/run` | 运行回测 |
| GET | `/backtest/results` | 获取回测结果 |

### 数据管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/data/download` | 下载数据 |
| GET | `/data/list` | 列出已下载数据 |

### 策略管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/strategies/list` | 列出所有策略 |

### 日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/logs/recent` | 获取最近日志 |
| GET | `/logs/errors` | 获取错误日志 |

### 交易记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/trades/show` | 显示交易记录 |

---

## 💡 使用示例

### 1. 启动交易

```bash
curl -X POST "http://localhost:8000/trade/start" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "ichiV1"}'
```

### 2. 获取状态

```bash
curl "http://localhost:8000/trade/status"
```

### 3. 运行回测

```bash
curl -X POST "http://localhost:8000/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "ichiV1",
    "timerange": "20240901-20240930"
  }'
```

### 4. 下载数据

```bash
curl -X POST "http://localhost:8000/data/download" \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": ["BTC/USDT:USDT", "ETH/USDT:USDT"],
    "timeframes": ["5m", "1h"],
    "days": 30
  }'
```

### 5. 获取日志

```bash
curl "http://localhost:8000/logs/recent?lines=50"
```

---

## 🎨 前端集成示例

### JavaScript/Fetch

```javascript
// 启动交易
async function startTrade(strategy) {
  const response = await fetch('http://localhost:8000/trade/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ strategy })
  });
  return await response.json();
}

// 获取状态
async function getStatus() {
  const response = await fetch('http://localhost:8000/trade/status');
  return await response.json();
}

// 使用
startTrade('ichiV1').then(data => console.log(data));
```

### Python/Requests

```python
import requests

# 启动交易
response = requests.post(
    'http://localhost:8000/trade/start',
    json={'strategy': 'ichiV1'}
)
print(response.json())

# 获取状态
response = requests.get('http://localhost:8000/trade/status')
print(response.json())
```

### Vue.js 示例

```vue
<template>
  <div>
    <button @click="startTrade">启动交易</button>
    <button @click="getStatus">查看状态</button>
    <pre>{{ status }}</pre>
  </div>
</template>

<script>
export default {
  data() {
    return {
      status: null
    }
  },
  methods: {
    async startTrade() {
      const res = await fetch('http://localhost:8000/trade/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy: 'ichiV1' })
      });
      const data = await res.json();
      alert(data.message);
    },
    async getStatus() {
      const res = await fetch('http://localhost:8000/trade/status');
      this.status = await res.json();
    }
  }
}
</script>
```

---

## 🔒 安全建议

### 生产环境配置

1. **添加认证**
```python
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.get("/protected")
async def protected_route(credentials: HTTPBearer = Depends(security)):
    # 验证 token
    pass
```

2. **限制 CORS**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # 指定域名
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

3. **使用 HTTPS**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 \
  --ssl-keyfile=./key.pem \
  --ssl-certfile=./cert.pem
```

4. **添加速率限制**
```bash
pip install slowapi
```

---

## 📁 目录结构

```
api/
├── main.py              # FastAPI 主应用
├── requirements.txt     # Python 依赖
├── start.sh            # 启动脚本
└── README.md           # 本文档
```

---

## 🐛 故障排查

### 问题 1: 端口被占用

```bash
# 查看占用端口的进程
lsof -i :8000

# 更换端口
uvicorn main:app --port 8001
```

### 问题 2: 容器名称不匹配

修改 `main.py` 中的 `CONTAINER_NAME` 变量：
```python
CONTAINER_NAME = "你的容器名"
```

### 问题 3: 权限问题

```bash
# 给启动脚本添加执行权限
chmod +x start.sh
```

---

## 🚀 进阶配置

### 后台运行

```bash
# 使用 nohup
nohup python3 main.py > api.log 2>&1 &

# 使用 systemd (推荐)
# 创建 /etc/systemd/system/freqtrade-api.service
```

### Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📝 开发说明

### 添加新端点

```python
@app.get("/my/endpoint")
async def my_endpoint():
    return {"message": "Hello World"}
```

### 修改容器名

编辑 `main.py`:
```python
CONTAINER_NAME = "你的容器名"
```

---

## 🎯 TODO

- [ ] 添加 WebSocket 支持（实时日志）
- [ ] 添加用户认证
- [ ] 添加速率限制
- [ ] 添加数据缓存
- [ ] 添加更详细的错误处理
- [ ] 添加单元测试

---

## 📞 支持

如有问题，请查看：
- FastAPI 文档: https://fastapi.tiangolo.com/
- Freqtrade 文档: https://www.freqtrade.io/

---

**开始使用 Freqtrade API 吧！** 🚀
