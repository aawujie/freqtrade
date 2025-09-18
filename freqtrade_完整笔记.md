# Freqtrade 完整学习笔记

> 本文档整合了所有 Freqtrade 相关的学习资料，包括快速入门、配置指南、学习路径和知识点笔记。

## 📖 目录

1. [快速入门指南](#快速入门指南)
2. [配置指南](#配置指南)
3. [学习路径](#学习路径)
4. [知识点笔记](#知识点笔记)
5. [实用脚本](#实用脚本)

---

## 快速入门指南

### 🚀 5分钟快速上手

#### 1. 启动服务
```bash
docker compose up -d
```

#### 2. 访问 Web UI
打开浏览器：`http://localhost:8080`
- 用户名：`freqtrader`
- 密码：`123`

#### 3. 查看实时交易
在 Web UI 中查看：
- 当前持仓
- 交易历史
- 盈亏统计

### 📊 运行第一个回测

#### 1. 下载数据
```bash
freqtrade download-data \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --timeframes 5m \
  --days 10
```

#### 2. 运行回测
```bash
freqtrade backtesting \
  --config /freqtrade/user_data/config_backtest.json \
  --strategy SampleStrategy \
  --timerange 20250907-20250917 \
  --export trades
```

#### 3. 查看结果
- 在 Web UI 的 "Backtest" 页面查看详细结果
- 或查看 `user_data/backtest_results/` 目录

### 🔧 常用命令速查

| 功能 | 命令 |
|------|------|
| 启动服务 | `docker compose up -d` |
| 停止服务 | `docker compose down` |
| 查看状态 | `docker compose ps` |
| 查看日志 | `docker compose logs -f freqtrade` |
| 下载数据 | `freqtrade download-data --pairs BTC/USDT:USDT --timeframes 5m --days 30` |
| 运行回测 | `freqtrade backtesting --strategy SampleStrategy --timerange 20240901-20240930` |
| 查看策略 | `freqtrade list-strategies` |

### ⚠️ 重要提醒

1. **默认是模拟交易模式** (`dry_run: true`)
2. **实盘交易前请充分测试**
3. **注意风险管理**
4. **定期备份配置**

### 🆘 遇到问题？

1. 查看日志：`docker compose logs freqtrade`
2. 检查容器状态：`docker compose ps`
3. 重启服务：`docker compose restart`
4. 查看完整文档：`README.md`

---

## 配置指南

### 📁 配置文件结构

```
user_data/
├── config.json              # 主配置文件
├── config_backtest.json     # 回测专用配置
├── strategies/              # 策略文件目录
├── data/                    # 市场数据目录
├── backtest_results/        # 回测结果目录
└── logs/                    # 日志文件目录
```

### ⚙️ 主配置文件详解

#### 基础交易设置

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

#### 交易所配置

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

#### 风险管理设置

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

#### API 服务器配置

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

#### 绘图配置

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

### 🔧 配置参数说明

#### 交易参数

| 参数 | 说明 | 推荐值 | 注意事项 |
|------|------|--------|----------|
| `max_open_trades` | 最大同时交易数量 | 3-10 | 根据资金量调整 |
| `stake_amount` | 每次交易金额 | 100-1000 | 不要超过总资金的 10% |
| `stake_currency` | 基础货币 | USDT | 选择流动性好的货币 |
| `dry_run` | 模拟交易模式 | true | 新手建议开启 |

#### 风险参数

| 参数 | 说明 | 推荐值 | 说明 |
|------|------|--------|------|
| `stoploss` | 止损比例 | -0.1 | 10% 止损 |
| `minimal_roi` | 最小收益率 | {"0": 0.04} | 4% 止盈 |
| `trailing_stop` | 追踪止损 | false | 高级功能 |
| `tradable_balance_ratio` | 可用资金比例 | 0.99 | 保留 1% 缓冲 |

#### 交易所参数

| 参数 | 说明 | 示例值 | 说明 |
|------|------|--------|------|
| `name` | 交易所名称 | binance | 支持 100+ 交易所 |
| `key` | API Key | your_key | 从交易所获取 |
| `secret` | API Secret | your_secret | 保密存储 |
| `pair_whitelist` | 交易对白名单 | ["BTC/USDT:USDT"] | 限制交易范围 |

### 🎯 不同场景配置

#### 新手配置

```json
{
  "max_open_trades": 1,
  "stake_amount": 50,
  "dry_run": true,
  "stoploss": -0.05,
  "minimal_roi": {"0": 0.02}
}
```

#### 进阶配置

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

#### 专业配置

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

### 🔍 配置验证

#### 检查配置语法

```bash
# 验证配置文件
docker compose exec freqtrade freqtrade show-config

# 测试配置
docker compose exec freqtrade freqtrade test-pairlist
```

#### 常见配置错误

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

### 📝 配置最佳实践

#### 1. 安全配置

```json
{
  "api_server": {
    "username": "strong_username",
    "password": "strong_password_123!",
    "jwt_secret_key": "very_long_random_string_here"
  }
}
```

#### 2. 性能优化

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

#### 3. 日志配置

```json
{
  "verbosity": 3,
  "logfile": "user_data/logs/freqtrade.log"
}
```

### 🚨 重要提醒

1. **备份配置**：修改前备份原配置文件
2. **逐步测试**：先小金额测试，再增加投入
3. **监控日志**：定期检查交易日志
4. **风险控制**：设置合理的止损和止盈
5. **API 安全**：不要泄露 API 密钥

---

## 学习路径

### 🎯 学习目标
从零基础到熟练使用 Freqtrade，按照难度递增的顺序学习。

### 📚 学习阶段

#### 阶段1：基础入门（必学）
**目标**：能够启动服务，查看基本状态

##### 1.1 服务管理
```bash
# 启动服务
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f freqtrade

# 停止服务
docker compose down
```

##### 1.2 基础信息查看（容器内执行）
```bash
# 查看配置
freqtrade show-config

# 查看可用交易所
freqtrade list-exchanges

# 查看可用策略
freqtrade list-strategies
```

**学习重点**：
- 理解 Docker 容器操作
- 熟悉基本命令格式
- 了解配置文件结构

#### 阶段2：数据管理（重要）
**目标**：能够下载和管理市场数据

##### 2.1 数据下载
```bash
# 下载单个交易对数据
freqtrade download-data \
  --pairs BTC/USDT:USDT \
  --timeframes 5m \
  --days 30

# 下载多个交易对数据
freqtrade download-data \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --timeframes 5m 1h \
  --days 30
```

##### 2.2 数据管理
```bash
# 查看已下载的数据
freqtrade list-data

# 清理数据
freqtrade clean-data
```

**学习重点**：
- 理解时间框架（timeframes）
- 掌握数据下载参数
- 学会数据管理

#### 阶段3：回测分析（核心）
**目标**：能够运行回测并分析结果

##### 3.1 基础回测
```bash
# 运行简单回测
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240901-20240930

# 导出交易数据
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240901-20240930 \
  --export trades
```

##### 3.2 回测结果分析
```bash
# 查看回测结果
freqtrade backtesting-show

# 查看交易记录
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

**学习重点**：
- 理解回测概念
- 掌握时间范围设置
- 学会分析回测结果

#### 阶段4：策略开发（进阶）
**目标**：能够创建和修改交易策略

##### 4.1 策略创建
```bash
# 创建新策略
freqtrade new-strategy --strategy MyStrategy

# 测试策略语法
freqtrade test-pairlist
```

##### 4.2 策略优化
```bash
# 参数优化
freqtrade hyperopt \
  --strategy MyStrategy \
  --epochs 100

# 查看优化结果
freqtrade hyperopt-list
```

**学习重点**：
- 理解策略结构
- 掌握技术指标
- 学会参数优化

#### 阶段5：可视化分析（实用）
**目标**：能够使用图表和 Web UI 分析

##### 5.1 Web UI 使用
```bash
# 安装 Web UI
freqtrade install-ui

# 启动 Web 服务器
freqtrade webserver
```

##### 5.2 图表分析
```bash
# 生成 K线图
freqtrade plot-dataframe \
  --strategy SampleStrategy \
  --pairs BTC/USDT:USDT

# 生成盈亏图
freqtrade plot-profit
```

**学习重点**：
- 使用 Web UI 界面
- 理解图表分析
- 掌握可视化工具

#### 阶段6：高级功能（专业）
**目标**：掌握高级功能和故障排除

##### 6.1 数据转换
```bash
# 转换数据格式
freqtrade convert-data \
  --format-from json \
  --format-to feather

# 转换交易数据
freqtrade convert-trade-data
```

##### 6.2 数据库管理
```bash
# 数据库迁移
freqtrade convert-db

# 策略更新
freqtrade strategy-updater
```

##### 6.3 高级分析
```bash
# 前瞻性偏差分析
freqtrade lookahead-analysis

# 递归公式分析
freqtrade recursive-analysis
```

**学习重点**：
- 数据格式转换
- 数据库管理
- 高级分析工具

### 🎯 学习建议

#### 新手建议
1. **先学阶段1-2**：掌握基础操作
2. **重点学阶段3**：回测是核心功能
3. **实践为主**：多动手操作
4. **记录笔记**：记录重要命令和参数

#### 进阶建议
1. **深入阶段4**：策略开发是关键
2. **熟练阶段5**：可视化分析很重要
3. **了解阶段6**：高级功能按需学习

#### 学习资源
- **官方文档**：https://www.freqtrade.io/
- **社区论坛**：Discord、Reddit
- **示例策略**：学习现有策略代码

### 📋 学习检查清单

#### 基础阶段 ✅
- [ ] 能够启动和停止服务
- [ ] 能够查看配置和状态
- [ ] 能够下载市场数据
- [ ] 能够运行简单回测

#### 进阶阶段 ✅
- [ ] 能够分析回测结果
- [ ] 能够创建自定义策略
- [ ] 能够使用 Web UI
- [ ] 能够生成分析图表

#### 高级阶段 ✅
- [ ] 能够进行参数优化
- [ ] 能够处理数据转换
- [ ] 能够进行高级分析
- [ ] 能够排除常见问题

### 🚀 快速开始

#### 第1天：基础操作
```bash
# 1. 启动服务
docker compose up -d

# 2. 查看状态
docker compose ps

# 3. 访问 Web UI
# 打开浏览器：http://localhost:8080
```

#### 第2天：数据下载
```bash
# 下载测试数据
freqtrade download-data \
  --pairs BTC/USDT:USDT \
  --timeframes 5m \
  --days 7
```

#### 第3天：运行回测
```bash
# 运行第一个回测
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240910-20240917
```

#### 第4天：分析结果
```bash
# 查看回测结果
freqtrade backtesting-show

# 查看交易记录
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

---

## 知识点笔记

### 📚 SQLite URI 格式详解

#### 基本格式
```
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

#### 格式分解
| 部分 | 说明 | 示例 |
|------|------|------|
| `sqlite://` | 协议标识符 | 表示这是 SQLite 数据库 |
| `///` | 路径分隔符 | 三个斜杠表示绝对路径 |
| `/freqtrade/user_data/tradesv3.dryrun.sqlite` | 实际文件路径 | 容器内的绝对路径 |

#### 路径格式对比

##### 1. 相对路径格式（不推荐）
```bash
sqlite:///tradesv3.dryrun.sqlite
```

##### 2. 绝对路径格式（推荐）
```bash
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

##### 3. 本地文件系统路径
```bash
/Users/apple/code/freqtrade/user_data/tradesv3.dryrun.sqlite
```

#### 容器内路径映射

| 容器内路径 | 本地路径 | 说明 |
|------------|----------|------|
| `/freqtrade/user_data/` | `/Users/apple/code/freqtrade/user_data/` | 用户数据目录 |
| `/freqtrade/user_data/tradesv3.dryrun.sqlite` | `/Users/apple/code/freqtrade/user_data/tradesv3.dryrun.sqlite` | 模拟交易数据库 |
| `/freqtrade/user_data/tradesv3.sqlite` | `/Users/apple/code/freqtrade/user_data/tradesv3.sqlite` | 实盘交易数据库 |

#### SQLite 文件类型说明

| 文件扩展名 | 说明 | 作用 |
|------------|------|------|
| `.sqlite` | 主数据库文件 | 存储实际数据 |
| `.sqlite-shm` | 共享内存文件 | 多进程访问时的共享内存 |
| `.sqlite-wal` | 预写日志文件 | 事务日志，提高性能 |

#### 实际应用命令

##### 查看模拟交易记录
```bash
docker compose exec freqtrade freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

##### 查看实盘交易记录
```bash
docker compose exec freqtrade freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
```

#### 记忆技巧
```
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
│       │  │
│       │  └─ 容器内绝对路径
│       └─ 三个斜杠 = 绝对路径
└─ SQLite 协议
```

#### 为什么使用这种格式？

1. **协议标识**：`sqlite://` 告诉程序这是 SQLite 数据库
2. **绝对路径**：`///` 确保路径从根目录开始
3. **容器兼容**：在 Docker 容器内使用绝对路径
4. **跨平台**：URI 格式在不同操作系统间保持一致

### 🔧 常用命令速查

#### 数据库相关命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `show-trades` | 查看交易记录 | `freqtrade show-trades --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite` |
| `test-pairlist` | 测试交易对列表 | `freqtrade test-pairlist` |
| `list-strategies` | 列出所有策略 | `freqtrade list-strategies` |

#### 配置相关命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `show-config` | 显示当前配置 | `freqtrade show-config` |
| `test-pairlist` | 验证交易对配置 | `freqtrade test-pairlist` |

### 📝 重要提醒

#### 数据库选择
- **模拟交易模式** (`dry_run: true`) → 使用 `tradesv3.dryrun.sqlite`
- **实盘交易模式** (`dry_run: false`) → 使用 `tradesv3.sqlite`

#### 路径格式
- 容器内使用：`sqlite:////freqtrade/user_data/...`
- 本地使用：`sqlite:////Users/username/path/...`
- 相对路径：`sqlite:///filename.sqlite`（不推荐）

#### 安全注意事项
- 不要将数据库文件提交到版本控制
- 定期备份重要的交易数据
- 注意数据库文件的权限设置

### 🎯 快速参考

#### 常用数据库路径
```bash
# 模拟交易数据库
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite

# 实盘交易数据库
sqlite:////freqtrade/user_data/tradesv3.sqlite

# 本地数据库（示例）
sqlite:////Users/username/freqtrade/user_data/tradesv3.sqlite
```

---

## 实用脚本

### 交易记录查看脚本

以下是一个便捷的 shell 脚本，用于自动检测交易模式并查看相应的交易记录：

```bash
#!/bin/bash

# Freqtrade 交易记录查看脚本

echo "🔍 检查交易模式..."

# 检查是否为模拟交易模式
if grep -q '"dry_run": true' user_data/config.json; then
    echo "📊 当前为模拟交易模式，查看模拟交易记录..."
    freqtrade show-trades \
        --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
else
    echo "💰 当前为实盘交易模式，查看实盘交易记录..."
    freqtrade show-trades \
        --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
fi
```

#### 使用方法
1. 将脚本保存为 `show-trades.sh`
2. 给脚本添加执行权限：`chmod +x show-trades.sh`
3. 运行脚本：`./show-trades.sh`

---

## 📚 总结

本文档整合了 Freqtrade 的完整学习资料，包括：

1. **快速入门**：5分钟上手指南
2. **详细配置**：完整的配置参数说明
3. **学习路径**：从基础到高级的系统学习计划
4. **知识点笔记**：重要概念和技术细节
5. **实用脚本**：提高效率的工具脚本

### 🎯 学习建议

1. **按顺序学习**：从快速入门开始，逐步深入
2. **实践为主**：每个知识点都要动手操作
3. **记录笔记**：记录自己的操作经验和问题
4. **持续更新**：随着学习深入，不断完善笔记

### 🚀 开始行动

现在就开始你的 Freqtrade 量化交易之旅吧！

---

**最后更新**: 2025-09-18  
**版本**: 1.0  
**整合自**: docs/ 目录下的所有文档
