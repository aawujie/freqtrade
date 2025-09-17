# Freqtrade 配置指南

## 📁 配置文件结构

```
user_data/
├── config.json              # 主配置文件
├── config_backtest.json     # 回测专用配置
├── strategies/              # 策略文件目录
├── data/                    # 市场数据目录
├── backtest_results/        # 回测结果目录
└── logs/                    # 日志文件目录
```

## ⚙️ 主配置文件详解

### 基础交易设置

```json
{
  "max_open_trades": 3,           // 最大同时交易数量
  "stake_currency": "USDT",       // 基础货币
  "stake_amount": 100,            // 每次交易金额
  "tradable_balance_ratio": 0.99, // 可用资金比例
  "dry_run": true,                // 模拟交易模式
  "dry_run_wallet": 1000,         // 模拟钱包金额
  "trading_mode": "futures",      // 交易模式：spot/futures
  "margin_mode": "isolated"       // 保证金模式：isolated/cross
}
```

### 交易所配置

```json
{
  "exchange": {
    "name": "binance",            // 交易所名称
    "key": "your_api_key",        // API Key
    "secret": "your_secret",      // API Secret
    "pair_whitelist": [           // 交易对白名单
      "BTC/USDT:USDT",
      "ETH/USDT:USDT"
    ],
    "pair_blacklist": [           // 交易对黑名单
      "BNB/.*"
    ]
  }
}
```

### 风险管理设置

```json
{
  "stoploss": -0.1,               // 止损比例 (-10%)
  "trailing_stop": false,         // 是否启用追踪止损
  "trailing_stop_positive": 0.02, // 追踪止损正偏移
  "trailing_stop_positive_offset": 0.02,
  "trailing_only_offset_is_reached": false,
  "minimal_roi": {                // 最小收益率
    "60": 0.01,                   // 60分钟后 1%
    "30": 0.02,                   // 30分钟后 2%
    "0": 0.04                     // 立即 4%
  }
}
```

### API 服务器配置

```json
{
  "api_server": {
    "enabled": true,              // 启用 API 服务器
    "listen_ip_address": "0.0.0.0", // 监听地址
    "listen_port": 8080,          // 监听端口
    "username": "freqtrader",     // Web UI 用户名
    "password": "123",            // Web UI 密码
    "jwt_secret_key": "your_jwt_secret",
    "ws_token": "your_ws_token"
  }
}
```

### 绘图配置

```json
{
  "plot_config": {
    "main_plot": {                // 主图指标
      "sma20": {"color": "blue"},
      "ema50": {"color": "orange"}
    },
    "subplots": {                 // 副图指标
      "RSI": {
        "rsi": {"color": "red"}
      },
      "MACD": {
        "macd": {"color": "blue"},
        "macdsignal": {"color": "red"},
        "macdhist": {
          "type": "bar",
          "plotly": {"opacity": 0.9}
        }
      }
    }
  }
}
```

## 🔧 配置参数说明

### 交易参数

| 参数 | 说明 | 推荐值 | 注意事项 |
|------|------|--------|----------|
| `max_open_trades` | 最大同时交易数量 | 3-10 | 根据资金量调整 |
| `stake_amount` | 每次交易金额 | 100-1000 | 不要超过总资金的 10% |
| `stake_currency` | 基础货币 | USDT | 选择流动性好的货币 |
| `dry_run` | 模拟交易模式 | true | 新手建议开启 |

### 风险参数

| 参数 | 说明 | 推荐值 | 说明 |
|------|------|--------|------|
| `stoploss` | 止损比例 | -0.1 | 10% 止损 |
| `minimal_roi` | 最小收益率 | {"0": 0.04} | 4% 止盈 |
| `trailing_stop` | 追踪止损 | false | 高级功能 |
| `tradable_balance_ratio` | 可用资金比例 | 0.99 | 保留 1% 缓冲 |

### 交易所参数

| 参数 | 说明 | 示例值 | 说明 |
|------|------|--------|------|
| `name` | 交易所名称 | binance | 支持 100+ 交易所 |
| `key` | API Key | your_key | 从交易所获取 |
| `secret` | API Secret | your_secret | 保密存储 |
| `pair_whitelist` | 交易对白名单 | ["BTC/USDT:USDT"] | 限制交易范围 |

## 🎯 不同场景配置

### 新手配置

```json
{
  "max_open_trades": 1,
  "stake_amount": 50,
  "dry_run": true,
  "stoploss": -0.05,
  "minimal_roi": {"0": 0.02}
}
```

### 进阶配置

```json
{
  "max_open_trades": 5,
  "stake_amount": 200,
  "dry_run": false,
  "stoploss": -0.1,
  "trailing_stop": true,
  "minimal_roi": {"60": 0.01, "30": 0.02, "0": 0.04}
}
```

### 专业配置

```json
{
  "max_open_trades": 10,
  "stake_amount": 500,
  "dry_run": false,
  "stoploss": -0.15,
  "trailing_stop": true,
  "trailing_stop_positive": 0.02,
  "minimal_roi": {"120": 0.005, "60": 0.01, "30": 0.02, "0": 0.05}
}
```

## 🔍 配置验证

### 检查配置语法

```bash
# 验证配置文件
docker compose exec freqtrade freqtrade show-config

# 测试配置
docker compose exec freqtrade freqtrade test-pairlist
```

### 常见配置错误

1. **API 配置错误**
   ```json
   // ❌ 错误
   "key": "",
   "secret": ""
   
   // ✅ 正确
   "key": "your_real_api_key",
   "secret": "your_real_secret"
   ```

2. **交易对格式错误**
   ```json
   // ❌ 错误
   "pair_whitelist": ["BTCUSDT"]
   
   // ✅ 正确
   "pair_whitelist": ["BTC/USDT:USDT"]
   ```

3. **金额设置错误**
   ```json
   // ❌ 错误
   "stake_amount": 0
   
   // ✅ 正确
   "stake_amount": 100
   ```

## 📝 配置最佳实践

### 1. 安全配置

```json
{
  "api_server": {
    "username": "strong_username",
    "password": "strong_password_123!",
    "jwt_secret_key": "very_long_random_string_here"
  }
}
```

### 2. 性能优化

```json
{
  "internals": {
    "process_throttle_secs": 5
  },
  "unfilledtimeout": {
    "entry": 10,
    "exit": 10,
    "unit": "minutes"
  }
}
```

### 3. 日志配置

```json
{
  "verbosity": 3,
  "logfile": "user_data/logs/freqtrade.log"
}
```

## 🚨 重要提醒

1. **备份配置**：修改前备份原配置文件
2. **逐步测试**：先小金额测试，再增加投入
3. **监控日志**：定期检查交易日志
4. **风险控制**：设置合理的止损和止盈
5. **API 安全**：不要泄露 API 密钥

---

**配置完成后，记得重启服务使配置生效！**
