# Freqtrade 命令手册 - 实用指南

## 📋 目录

- 常用命令速查
- 服务管理命令
- 数据管理命令
- 回测分析命令
- 策略开发命令
- 交易管理命令
- 数据库操作命令
- 可视化工具命令
- 高级功能命令
- 实用脚本工具
- 知识点笔记

---

## 🔧 常用命令速查

| 分类                 | 命令                                      | 用途                | 快速示例           |
| -------------------- | ----------------------------------------- | ------------------- | ------------------ |
| **服务管理**   | `docker compose up -d`                  | 启动 Freqtrade 服务 | 后台启动容器       |
|                      | `docker compose logs -f`                | 查看服务日志        | 实时监控日志       |
|                      | `freqtrade show-config`                 | 显示当前配置        | 检查配置参数       |
|                      | `freqtrade list-exchanges`              | 查看支持交易所      | 了解可用交易所     |
| **数据管理**   | `freqtrade download-data`               | 下载市场数据        | 下载 BTC/USDT 数据 |
|                      | `freqtrade list-data`                   | 查看已下载数据      | 检查数据状态       |
|                      | `freqtrade clean-data`                  | 清理过期数据        | 释放存储空间       |
| **回测分析**   | `freqtrade backtesting`                 | 运行策略回测        | 测试策略表现       |
|                      | `freqtrade backtesting-show`            | 查看回测结果        | 分析策略收益       |
|                      | `freqtrade backtesting-show --index -1` | 查看最新回测        | 快速检查结果       |
| **策略开发**   | `freqtrade new-strategy`                | 创建新策略          | 生成策略模板       |
|                      | `freqtrade list-strategies`             | 列出所有策略        | 查看可用策略       |
|                      | `freqtrade test-pairlist`               | 测试策略配置        | 验证策略语法       |
|                      | `freqtrade hyperopt`                    | 参数优化            | 自动调参优化       |
| **交易管理**   | `freqtrade show-trades`                 | 查看交易记录        | 检查交易历史       |
|                      | `freqtrade trade`                       | 启动交易机器人      | 开始自动交易       |
|                      | `freqtrade stop`                        | 停止交易机器人      | 安全停止交易       |
| **数据库操作** | `freqtrade show-trades --db-url`        | 指定数据库查询      | 选择特定数据库     |
|                      | `freqtrade convert-db`                  | 数据库迁移          | 升级数据库格式     |
| **可视化工具** | `freqtrade webserver`                   | 启动 Web UI         | 浏览器管理界面     |
|                      | `freqtrade plot-dataframe`              | 生成策略图表        | 可视化策略表现     |
|                      | `freqtrade plot-profit`                 | 生成盈亏图表        | 分析收益曲线       |
| **高级功能**   | `freqtrade lookahead-analysis`          | 前瞻性偏差分析      | 检查策略公平性     |
|                      | `freqtrade recursive-analysis`          | 递归公式分析        | 验证策略逻辑       |
|                      | `freqtrade convert-data`                | 数据格式转换        | 转换数据格式       |

### 📝 重要提醒

#### 数据库选择

- **模拟交易** (`dry_run: true`) → 使用 `tradesv3.dryrun.sqlite`
- **实盘交易** (`dry_run: false`) → 使用 `tradesv3.sqlite`

#### 安全注意事项

- 🔒 不要将数据库文件提交到版本控制
- 💾 定期备份重要的交易数据
- ⚡ 注意数据库文件的权限设置
- 🛡️ 使用强密码保护 Web UI

#### 数据库路径

```
模拟交易: sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
实盘交易: sqlite:////freqtrade/user_data/tradesv3.sqlite
```

---

## 服务管理命令

### Docker 容器管理

```bash
# 启动 Freqtrade 服务
docker compose up -d

# 停止服务
docker compose down

# 查看服务状态
docker compose ps

# 查看服务日志
docker compose logs -f freqtrade

# 重启服务
docker compose restart

# 进入容器
docker exec -it freqtrade /bin/bash
```

### Freqtrade 状态查询

```bash
# 查看当前配置
freqtrade show-config

# 查看可用交易所
freqtrade list-exchanges

# 查看可用策略
freqtrade list-strategies

# 查看可用时间框架
freqtrade list-timeframes
```

---

## 数据管理命令

### 数据下载

```bash
# 下载单个交易对数据
freqtrade download-data \
  --pairs BTC/USDT:USDT \
  --timeframes 5m \
  --days 30 \
  --timerange 20240101-20241231 \  用 days 或 timerange

# 下载多个交易对数据
freqtrade download-data \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --timeframes 5m 1h \
  --days 30

# 下载特定交易所数据
freqtrade download-data \
  --exchange binance \
  --pairs BTC/USDT:USDT \
  --timeframes 5m 1h 4h \
  --days 100
```

### 数据管理

```bash
# 查看已下载的数据
freqtrade list-data --show-timerange

# 清理过期数据
freqtrade clean-data

# 显示数据统计信息
freqtrade list-data --exchange binance
```

---

## 回测分析命令

### 基础回测

```bash
# 运行简单回测
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240901-20240930

# 指定配置文件
freqtrade backtesting \
  --config /freqtrade/user_data/config_backtest.json \
  --strategy SampleStrategy \
  --timerange 20240901-20240930

# 导出交易数据
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240901-20240930 \
  --export trades

# 启用最大开仓数限制
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240901-20240930 \
  --max-open-trades 5
```

### 回测结果分析

```bash
# 查看回测结果摘要
freqtrade backtesting-show

# 查看特定策略的结果
freqtrade backtesting-show --strategy SampleStrategy

# 查看最近的回测结果
freqtrade backtesting-show --index -1
```

### 高级回测选项

```bash
# 自定义手续费
freqtrade backtesting \
  --strategy SampleStrategy \
  --fee 0.001

# 启用详细日志
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20240901-20240930 \
  --verbosity 2

# 自定义 stake 金额
freqtrade backtesting \
  --strategy SampleStrategy \
  --stake-amount 100
```

---

## 策略开发命令

### 策略创建和管理

```bash
# 创建新策略
freqtrade new-strategy --strategy MyStrategy

# 列出所有策略
freqtrade list-strategies

# 测试策略语法
freqtrade test-pairlist --strategy MyStrategy

# 验证策略配置
freqtrade test-pairlist --strategy MyStrategy --verbosity 2
```

### 策略优化

```bash
# 参数优化（基本）
freqtrade hyperopt \
  --strategy MyStrategy \
  --epochs 100

# 指定优化空间
freqtrade hyperopt \
  --strategy MyStrategy \
  --hyperopt-loss SharpeHyperOptLoss \
  --epochs 200 \
  # optional
  --spaces sell # 只优化卖出参数 (--spaces sell) 
  --spaces all # 优化所有参数 (--spaces all 或不指定)
  --spaces buy sell # 同时优化买入和卖出 (--spaces buy sell)

# 自定义时间范围
freqtrade hyperopt \
  --strategy MyStrategy \
  --timerange 20240101-20241231 \
  --epochs 100

# 优化结果分析
freqtrade hyperopt-list

# 显示最佳参数
freqtrade hyperopt-show --index 0
```

---

## 交易管理命令

### 交易记录查询

```bash
# 查看模拟交易记录
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite

# 查看实盘交易记录
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite

# 按策略筛选
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite \
  --strategy SampleStrategy

# 显示最近的交易
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite \
  -n 10
```

### 交易统计分析

```bash
# 查看盈亏统计
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite \
  --print-json

# 导出交易数据
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite \
  --export trades.csv
```

---

## 数据库操作命令

### 数据库相关命令

```bash
# 查看交易记录
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite

# 测试数据库连接
freqtrade test-pairlist

# 数据库迁移
freqtrade convert-db

# 转换交易数据格式
freqtrade convert-trade-data
```

### 数据库维护

```bash
# 查看数据库状态
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite \
  --print-json

# 清理数据库
# 注意：请谨慎使用，建议先备份
freqtrade convert-db --cleanup
```

---

## 可视化工具命令

### Web UI 管理

```bash
# 启动 Web 服务器
freqtrade webserver

# 自定义端口
freqtrade webserver --port 8081

# 指定配置文件
freqtrade webserver \
  --config /freqtrade/user_data/config.json
```

### 图表生成

```bash
# 生成策略回测图表
freqtrade plot-dataframe \
  --strategy SampleStrategy \
  --pairs BTC/USDT:USDT \
  --timerange 20240901-20240930

# 生成盈亏图表
freqtrade plot-profit \
  --pairs BTC/USDT:USDT \
  --timerange 20240901-20240930

# 生成多个交易对图表
freqtrade plot-dataframe \
  --strategy SampleStrategy \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --timerange 20240901-20240930
```

---

## 高级功能命令

### 数据转换

```bash
# 转换数据格式 (JSON → Feather)
freqtrade convert-data \
  --format-from json \
  --format-to feather

# 转换特定交易对数据
freqtrade convert-data \
  --pairs BTC/USDT:USDT \
  --format-from json \
  --format-to feather
```

### 系统分析

```bash
# 前瞻性偏差分析
freqtrade lookahead-analysis \
  --strategy SampleStrategy \
  --timerange 20240901-20240930

# 递归公式分析
freqtrade recursive-analysis \
  --strategy SampleStrategy \
  --timerange 20240901-20240930

# 策略更新检查
freqtrade strategy-updater \
  --strategy SampleStrategy
```

### 配置验证

```bash
# 验证策略配置
freqtrade test-pairlist \
  --strategy SampleStrategy \
  --verbosity 2

# 检查配置文件语法
freqtrade show-config \
  --config /freqtrade/user_data/config.json
```

---

## 实用脚本工具

### 交易记录查看脚本

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

## 知识点笔记

### 📚 SQLite URI 格式详解

#### 基本格式

```
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

#### 格式分解

| 部分                                            | 说明         | 示例                   |
| ----------------------------------------------- | ------------ | ---------------------- |
| `sqlite://`                                   | 协议标识符   | 表示这是 SQLite 数据库 |
| `///`                                         | 路径分隔符   | 三个斜杠表示绝对路径   |
| `/freqtrade/user_data/tradesv3.dryrun.sqlite` | 实际文件路径 | 容器内的绝对路径       |

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

| 容器内路径                                      | 本地路径                                                         | 说明           |
| ----------------------------------------------- | ---------------------------------------------------------------- | -------------- |
| `/freqtrade/user_data/`                       | `/Users/apple/code/freqtrade/user_data/`                       | 用户数据目录   |
| `/freqtrade/user_data/tradesv3.dryrun.sqlite` | `/Users/apple/code/freqtrade/user_data/tradesv3.dryrun.sqlite` | 模拟交易数据库 |
| `/freqtrade/user_data/tradesv3.sqlite`        | `/Users/apple/code/freqtrade/user_data/tradesv3.sqlite`        | 实盘交易数据库 |

#### SQLite 文件类型说明

| 文件扩展名      | 说明         | 作用                   |
| --------------- | ------------ | ---------------------- |
| `.sqlite`     | 主数据库文件 | 存储实际数据           |
| `.sqlite-shm` | 共享内存文件 | 多进程访问时的共享内存 |
| `.sqlite-wal` | 预写日志文件 | 事务日志，提高性能     |

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

---

## 📚 总结

本文档按照功能分类整合了 Freqtrade 的完整命令指南，包括：

1. **服务管理命令**：Docker 容器和 Freqtrade 基础操作
2. **数据管理命令**：市场数据下载、查看和管理
3. **回测分析命令**：策略回测运行和结果分析
4. **策略开发命令**：策略创建、测试和参数优化
5. **交易管理命令**：交易记录查询和统计分析
6. **数据库操作命令**：数据库查询、维护和管理
7. **可视化工具命令**：Web UI 和图表生成
8. **高级功能命令**：数据转换和系统分析
9. **实用脚本工具**：自动化脚本和工具
10. **知识点笔记**：SQLite 等技术细节详解

### 🎯 使用建议

1. **按需查找**：根据具体需求直接查看对应功能分类
2. **实践为主**：每个命令都要动手操作验证
3. **收藏常用**：将经常使用的命令加入书签
4. **版本更新**：关注 Freqtrade 新版本的命令变化

### 🚀 开始行动

现在就开始你的 Freqtrade 量化交易之旅吧！

---

**最后更新**: 2025-09-18
**版本**: 1.0
**整合自**: docs/ 目录下的所有文档
