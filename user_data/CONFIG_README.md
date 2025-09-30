# 配置文件使用说明

## 📁 配置文件结构

```
user_data/
├── config_composed.json             # ✅ 组合配置示例
├── config_backtest.json             # ✅ 原有回测配置
├── config_double_ma.json            # ✅ 双均线策略配置
├── config_ichiV1.json               # ✅ 一目均衡策略配置
└── configs/                         # 📁 模块化配置文件夹
    ├── config_base.json             # ✅ 基础通用配置
    ├── config_secrets.json          # ❌ 敏感信息（不提交Git）
    ├── config_secrets.json.example  # ✅ 敏感信息示例
    ├── config_pairs_spot.json       # ✅ 现货交易对列表
    ├── config_pairs_futures.json    # ✅ 合约交易对列表
    ├── config_plot.json             # ✅ 通用绘图配置
    ├── config_plot_minimal.json     # ✅ 最简绘图配置
    ├── config_plot_double_ma.json   # ✅ 双均线策略绘图
    └── config_plot_ichimoku.json    # ✅ 一目均衡策略绘图
```

## 🎯 快速开始

### 方法1: 使用命令行组合配置

```bash
# 现货交易
freqtrade trade \
    -c user_data/configs/config_base.json \
    -c user_data/configs/config_secrets.json \
    -c user_data/configs/config_pairs_spot.json \
    --strategy DoubleMAStrategy

# 合约交易
freqtrade trade \
    -c user_data/configs/config_base.json \
    -c user_data/configs/config_secrets.json \
    -c user_data/configs/config_pairs_futures.json \
    --strategy ichiV1
```

### 方法2: 使用组合配置文件（推荐）

```bash
# 使用预设的组合配置
freqtrade trade -c user_data/config_composed.json
```

## 🔧 配置文件详解

### configs/config_base.json - 基础配置
包含所有通用的交易参数：
- 最大开仓数、本金设置
- 订单定价策略
- 超时设置
- 基础 pairlists 配置

### configs/config_secrets.json - 敏感信息
⚠️ **重要**: 此文件包含 API 密钥，**不要提交到 Git**

包含：
- 交易所 API 密钥
- Telegram Token 和 Chat ID
- API Server 认证信息

### configs/config_pairs_spot.json - 现货交易对
包含现货市场的交易对列表和相关配置

### configs/config_pairs_futures.json - 合约交易对
包含合约市场的交易对列表和相关配置

### config_composed.json - 组合配置示例
演示如何使用 `add_config_files` 引入 configs/ 文件夹中的模块配置

## 🚀 使用示例

### 示例1: 双均线现货策略

创建 `config_double_ma_spot.json`:
```json
{
    "add_config_files": [
        "configs/config_base.json",
        "configs/config_secrets.json",
        "configs/config_pairs_spot.json"
    ],
    "strategy": "DoubleMAStrategy",
    "timeframe": "1h",
    "db_url": "sqlite:///trades_double_ma_spot.sqlite"
}
```

运行：
```bash
freqtrade trade -c user_data/config_double_ma_spot.json
```

### 示例2: 一目均衡合约策略

创建 `config_ichi_futures.json`:
```json
{
    "add_config_files": [
        "configs/config_base.json",
        "configs/config_secrets.json",
        "configs/config_pairs_futures.json"
    ],
    "strategy": "ichiV1",
    "timeframe": "5m",
    "max_open_trades": 2,
    "db_url": "sqlite:///trades_ichiV1.sqlite"
}
```

运行：
```bash
freqtrade trade -c user_data/config_ichi_futures.json
```

## 🔒 安全设置

### 1. 设置敏感信息文件

复制示例文件：
```bash
cp user_data/configs/config_secrets.json.example user_data/configs/config_secrets.json
```

编辑 `configs/config_secrets.json`，填入真实的 API 密钥

### 2. 验证 .gitignore

确保 `.gitignore` 包含：
```
user_data/configs/config_secrets.json
```

## 💡 最佳实践

1. **分离敏感信息**: 永远不要在通用配置中硬编码 API 密钥
2. **使用环境变量**: 在 `config_secrets.json` 中使用 `${FREQTRADE__*}` 格式
3. **模块化配置**: 按功能分离配置文件，提高复用性
4. **版本控制**: 提交示例配置（.example），不提交真实密钥
5. **配置验证**: 运行前使用 `freqtrade show-config` 验证配置

## 📚 详细文档

完整的配置文件包含指南，请查看：
- [配置文件包含指南](../docs/08-配置文件包含指南.md)
- [配置文件详解](../docs/01-配置文件详解.md)

---

✅ 配置文件已准备就绪，开始你的量化交易之旅吧！🚀
