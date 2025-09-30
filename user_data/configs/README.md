# Configs 文件夹说明

这个文件夹存放模块化的配置文件，用于组合和复用。

## 📁 文件说明

| 文件 | 用途 | 提交Git |
|------|------|---------|
| `config_base.json` | 基础通用交易参数 | ✅ 是 |
| `config_secrets.json` | 敏感信息（API密钥、Token等） | ❌ 否 |
| `config_secrets.json.example` | 敏感信息示例模板 | ✅ 是 |
| `config_pairs_spot.json` | 现货交易对列表 | ✅ 是 |
| `config_pairs_futures.json` | 合约交易对列表 | ✅ 是 |
| `config_plot.json` | 通用绘图配置 | ✅ 是 |
| `config_plot_minimal.json` | 最简绘图配置 | ✅ 是 |
| `config_plot_double_ma.json` | 双均线策略绘图配置 | ✅ 是 |
| `config_plot_ichimoku.json` | 一目均衡策略绘图配置 | ✅ 是 |
| `config_telegram.json` | Telegram 通知配置 | ✅ 是 |
| `config_telegram.json.example` | Telegram 配置示例 | ✅ 是 |
| `config_webhook.json` | Webhook 通知配置 | ✅ 是 |

## 🚀 快速使用

### 1. 设置敏感信息

```bash
# 复制示例文件
cp config_secrets.json.example config_secrets.json

# 编辑并填入真实的 API 密钥
vim config_secrets.json
```

### 2. 使用组合配置

```bash
# 使用根目录的组合配置（引用 configs 文件夹中的模块）
freqtrade trade -c user_data/config_composed.json
```

### 3. 创建自定义组合

在 user_data/ 根目录创建新的组合配置文件 `config_my_strategy.json`:

```json
{
    "add_config_files": [
        "configs/config_base.json",
        "configs/config_secrets.json",
        "configs/config_pairs_spot.json"
    ],
    "strategy": "MyStrategy",
    "timeframe": "1h",
    "db_url": "sqlite:///trades_my_strategy.sqlite"
}
```

## 📂 文件夹结构

```
user_data/
├── config_composed.json          ← 组合配置示例（引用 configs/ 中的模块）
└── configs/                      ← 模块化配置文件夹
    ├── README.md
    ├── config_base.json          ← 基础配置
    ├── config_secrets.json       ← 敏感信息（不提交Git）
    ├── config_secrets.json.example
    ├── config_pairs_spot.json
    └── config_pairs_futures.json
```

## 💡 路径说明

根目录的配置文件（如 `config_composed.json`）引用 configs/ 文件夹的文件：

- **引用 configs/ 文件夹的文件**: 使用 `configs/config_base.json`
- **引用多个模块**: 使用 `configs/config_secrets.json`、`configs/config_pairs_spot.json`
- **引用其他子文件夹**: 使用 `strategies/DoubleMAStrategy.json`

## 🔒 安全提示

⚠️ **重要**: `configs/config_secrets.json` 包含敏感信息，已添加到 `.gitignore`，请勿提交到版本控制！

---

查看完整文档: [配置文件包含指南](../../docs/08-配置文件包含指南.md)
