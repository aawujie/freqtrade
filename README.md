# Freqtrade 量化交易机器人使用指南

## 📋 目录
- [项目简介](#项目简介)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [策略开发](#策略开发)
- [回测分析](#回测分析)
- [可视化界面](#可视化界面)
- [实盘交易](#实盘交易)
- [常用命令](#常用命令)
- [故障排除](#故障排除)
- [注意事项](#注意事项)
- [文档目录](#文档目录)

## 🚀 项目简介

Freqtrade 是一个开源的加密货币量化交易机器人，支持多种交易所和策略。本项目基于 Docker 部署，提供完整的交易、回测和可视化功能。

### 主要特性
- ✅ 支持 100+ 交易所（Binance、OKX、Bybit 等）
- ✅ 策略回测和优化
- ✅ 实时交易监控
- ✅ Web UI 可视化界面
- ✅ 技术指标分析
- ✅ 风险管理工具

## 🔧 环境要求

- Docker & Docker Compose
- 至少 2GB 可用内存
- 稳定的网络连接

## 🏃‍♂️ 快速开始

### 1. 启动服务

```bash
# 启动 Freqtrade 容器
docker compose up -d

# 查看运行状态
docker compose ps
```

### 2. 访问 Web UI

打开浏览器访问：`http://localhost:8080`

**登录信息：**
- 用户名：`freqtrader`
- 密码：`123`

### 3. 查看实时状态

```bash
# 查看容器日志
docker compose logs -f freqtrade

# 查看交易状态
freqtrade status
```

## ⚙️ 配置说明

### 主配置文件：`user_data/config.json`

```json
{
  "max_open_trades": 3,           // 最大同时交易数量
  "stake_currency": "USDT",       // 基础货币
  "stake_amount": 100,            // 每次交易金额
  "dry_run": true,                // 模拟交易模式
  "trading_mode": "futures",      // 交易模式：spot/futures
  "exchange": {
    "name": "binance",            // 交易所名称
    "key": "your_api_key",        // API Key
    "secret": "your_secret"       // API Secret
  }
}
```

### 重要配置项说明

| 配置项 | 说明 | 推荐值 |
|--------|------|--------|
| `max_open_trades` | 最大同时交易数量 | 3-10 |
| `stake_amount` | 每次交易金额 | 100-1000 USDT |
| `dry_run` | 模拟交易模式 | 新手建议 true |
| `stoploss` | 止损比例 | -0.1 (10%) |
| `minimal_roi` | 最小收益率 | {"0": 0.04} |

## 📈 策略开发

### 策略文件位置
```
user_data/strategies/
├── sample_strategy.py    # 示例策略
└── your_strategy.py      # 您的自定义策略
```

### 创建自定义策略

```python
# user_data/strategies/my_strategy.py
from freqtrade.strategy import IStrategy

class MyStrategy(IStrategy):
    # 策略参数
    buy_rsi = 30
    sell_rsi = 70
    
    # 买入信号
    def populate_entry_trend(self, dataframe, metadata):
        dataframe.loc[
            (dataframe['rsi'] < self.buy_rsi),
            'enter_long'] = 1
        return dataframe
    
    # 卖出信号
    def populate_exit_trend(self, dataframe, metadata):
        dataframe.loc[
            (dataframe['rsi'] > self.sell_rsi),
            'exit_long'] = 1
        return dataframe
```

### 策略测试

```bash
# 测试策略语法
freqtrade test-pairlist

# 查看策略信息
freqtrade show-trades --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

## 📊 回测分析

### 1. 下载历史数据

```bash
# 下载 BTC 和 ETH 的 5 分钟数据（最近 30 天）
freqtrade download-data \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --timeframes 5m \
  --days 30
```

### 2. 运行回测

```bash
# 使用示例策略回测
freqtrade backtesting \
  --config /freqtrade/user_data/config_backtest.json \
  --strategy SampleStrategy \
  --timerange 20240901-20240930 \
  --export trades
```

### 3. 查看回测结果

回测结果保存在：`user_data/backtest_results/`

- **JSON 文件**：详细交易数据
- **ZIP 包**：完整回测环境
- **Web UI**：可视化图表

### 4. 回测结果解读

| 指标 | 说明 | 理想值 |
|------|------|--------|
| Total Profit % | 总收益率 | > 10% |
| Win Rate | 胜率 | > 50% |
| Sharpe Ratio | 夏普比率 | > 1.0 |
| Max Drawdown | 最大回撤 | < 20% |
| Profit Factor | 盈利因子 | > 1.5 |

## 🖥️ 可视化界面

### Web UI 功能

1. **Dashboard** - 实时交易概览
2. **Trade** - 交易管理
3. **Chart** - 技术分析图表
4. **Logs** - 系统日志

### 访问方式

```bash
# 本地访问
http://localhost:8080

# 远程访问（需要修改配置）
# 将 listen_ip_address 改为 0.0.0.0
```

### 图表功能

- K线图显示
- 技术指标叠加
- 买卖信号标记
- 回测结果可视化

## 💰 实盘交易

### ⚠️ 重要警告

**实盘交易有风险，请谨慎操作！**

### 1. 准备工作

```bash
# 1. 确保策略经过充分回测
# 2. 设置合理的风险参数
# 3. 准备充足的资金
# 4. 设置止损和止盈
```

### 2. 启用实盘交易

```json
// 修改 config.json
{
  "dry_run": false,              // 关闭模拟模式
  "exchange": {
    "key": "your_real_api_key",   // 使用真实 API
    "secret": "your_real_secret"
  }
}
```

### 3. 风险控制

```json
{
  "max_open_trades": 3,          // 限制同时交易数量
  "stake_amount": 100,           // 控制单次交易金额
  "stoploss": -0.1,              // 设置止损
  "minimal_roi": {"0": 0.04}     // 设置止盈
}
```

## 🛠️ 常用命令

### 容器管理

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f freqtrade
```

### 数据管理

```bash
# 下载数据
docker compose exec freqtrade freqtrade download-data \
  --pairs BTC/USDT:USDT \
  --timeframes 5m 1h \
  --days 30

# 查看数据
docker compose exec freqtrade freqtrade list-data

# 清理数据
docker compose exec freqtrade freqtrade clean-data
```

### 策略管理

```bash
# 列出所有策略
docker compose exec freqtrade freqtrade list-strategies

# 测试策略
docker compose exec freqtrade freqtrade test-pairlist \
  --strategy SampleStrategy

# 查看策略参数
docker compose exec freqtrade freqtrade show-trades \
  --strategy SampleStrategy
```

### 回测命令

```bash
# 基本回测
docker compose exec freqtrade freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240901-20240930

# 导出交易数据
docker compose exec freqtrade freqtrade backtesting \
  --strategy SampleStrategy \
  --export trades

# 参数优化
docker compose exec freqtrade freqtrade hyperopt \
  --strategy SampleStrategy \
  --epochs 100
```

## 🔍 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 检查 Docker 状态
docker --version
docker compose --version

# 检查端口占用
lsof -i :8080

# 重新构建镜像
docker compose build --no-cache
```

#### 2. API 连接问题

```bash
# 检查网络连接
docker compose exec freqtrade ping binance.com

# 验证 API 配置
docker compose exec freqtrade freqtrade show-config
```

#### 3. 数据下载失败

```bash
# 检查交易所连接
docker compose exec freqtrade freqtrade list-exchanges

# 手动下载数据
docker compose exec freqtrade freqtrade download-data \
  --pairs BTC/USDT:USDT \
  --timeframes 5m \
  --days 1
```

#### 4. Web UI 无法访问

```bash
# 检查容器状态
docker compose ps

# 检查端口映射
docker compose port freqtrade 8080

# 重启容器
docker compose restart freqtrade
```

### 日志分析

```bash
# 查看详细日志
docker compose logs --tail=100 freqtrade

# 实时监控日志
docker compose logs -f freqtrade

# 查看错误日志
docker compose logs freqtrade | grep ERROR
```

## ⚠️ 注意事项

### 安全提醒

1. **API 安全**
   - 不要将 API 密钥提交到版本控制
   - 使用只读权限的 API 密钥进行测试
   - 定期轮换 API 密钥

2. **资金安全**
   - 实盘交易前充分测试
   - 设置合理的止损和止盈
   - 不要投入超过承受能力的资金

3. **数据备份**
   - 定期备份配置文件
   - 保存重要的回测结果
   - 记录交易日志

### 性能优化

1. **资源使用**
   - 监控内存和 CPU 使用率
   - 合理设置 `max_open_trades`
   - 定期清理历史数据

2. **网络优化**
   - 使用稳定的网络连接
   - 考虑使用 VPS 部署
   - 配置合适的超时参数

### 法律合规

1. **了解当地法规**
   - 确保交易活动合法
   - 遵守税务规定
   - 注意反洗钱要求

2. **风险披露**
   - 加密货币交易风险极高
   - 可能损失全部投资
   - 请谨慎决策

## 📞 技术支持

### 官方资源

- **官方文档**: https://www.freqtrade.io/
- **GitHub**: https://github.com/freqtrade/freqtrade
- **Discord**: https://discord.gg/freqtrade
- **Telegram**: https://t.me/freqtrade

### 社区支持

- **Reddit**: r/freqtrade
- **Stack Overflow**: freqtrade 标签
- **中文社区**: 搜索 "freqtrade 中文"

---

## 📝 更新日志

- **2025-09-17**: 初始版本，包含基础配置和可视化功能
- **功能**: Web UI、回测分析、策略开发、实时监控

## 📚 文档目录

### 快速入门
- **[快速开始指南](docs/QUICKSTART.md)** - 5分钟快速上手
- **[学习路径指南](docs/LEARNING_PATH.md)** - 从零基础到精通的完整学习路径

### 配置指南
- **[配置详解](docs/CONFIG_GUIDE.md)** - 详细的配置参数说明和最佳实践

### 知识笔记
- **[知识点笔记](docs/KNOWLEDGE_NOTES.md)** - 重要概念和命令速查

### 实用工具
- **[show-trades.sh](docs/show-trades.sh)** - 便捷的交易记录查看脚本

---

**免责声明**: 本软件仅供学习和研究使用。加密货币交易存在高风险，可能导致资金损失。使用本软件进行实盘交易的风险由用户自行承担。
