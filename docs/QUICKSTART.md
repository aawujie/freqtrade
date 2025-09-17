# Freqtrade 快速入门指南

## 🚀 5分钟快速上手

### 1. 启动服务
```bash
docker compose up -d
```

### 2. 访问 Web UI
打开浏览器：`http://localhost:8080`
- 用户名：`freqtrader`
- 密码：`123`

### 3. 查看实时交易
在 Web UI 中查看：
- 当前持仓
- 交易历史
- 盈亏统计

## 📊 运行第一个回测

### 1. 下载数据
```bash
docker compose exec freqtrade freqtrade download-data \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --timeframes 5m \
  --days 10
```

### 2. 运行回测
```bash
docker compose exec freqtrade freqtrade backtesting \
  --config /freqtrade/user_data/config_backtest.json \
  --strategy SampleStrategy \
  --timerange 20250907-20250917 \
  --export trades
```

### 3. 查看结果
- 在 Web UI 的 "Backtest" 页面查看详细结果
- 或查看 `user_data/backtest_results/` 目录

## 🔧 常用命令速查

| 功能 | 命令 |
|------|------|
| 启动服务 | `docker compose up -d` |
| 停止服务 | `docker compose down` |
| 查看状态 | `docker compose ps` |
| 查看日志 | `docker compose logs -f freqtrade` |
| 下载数据 | `docker compose exec freqtrade freqtrade download-data --pairs BTC/USDT:USDT --timeframes 5m --days 30` |
| 运行回测 | `docker compose exec freqtrade freqtrade backtesting --strategy SampleStrategy --timerange 20240901-20240930` |
| 查看策略 | `docker compose exec freqtrade freqtrade list-strategies` |

## ⚠️ 重要提醒

1. **默认是模拟交易模式** (`dry_run: true`)
2. **实盘交易前请充分测试**
3. **注意风险管理**
4. **定期备份配置**

## 🆘 遇到问题？

1. 查看日志：`docker compose logs freqtrade`
2. 检查容器状态：`docker compose ps`
3. 重启服务：`docker compose restart`
4. 查看完整文档：`README.md`

---
**开始您的量化交易之旅！** 🎯
