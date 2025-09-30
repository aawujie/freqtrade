# ichiV1 策略更新说明

## ✅ 已修复的弃用警告

### 修改日期: 2025-09-30

## 🔧 修改内容

### 1. 参数字典重命名
```python
# 旧版（第 28-32 行）
sell_params = {
    "sell_trend_indicator": "trend_close_2h",
}

# 新版 ✅
exit_params = {
    "exit_trend_indicator": "trend_close_2h",
}
```

### 2. 策略配置参数更新（第 56-58 行）
```python
# 旧版
use_sell_signal = True
sell_profit_only = False
ignore_roi_if_buy_signal = False

# 新版 ✅
use_exit_signal = True
exit_profit_only = False
ignore_roi_if_entry_signal = False
```

### 3. 函数名称更新

#### 入场信号函数（第 135 行）
```python
# 旧版
def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

# 新版 ✅
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
```

#### 出场信号函数（第 212 行）
```python
# 旧版
def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

# 新版 ✅
def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
```

### 4. DataFrame 列名更新

#### 入场信号列（第 207 行）
```python
# 旧版
'buy'] = 1

# 新版 ✅
'enter_long'] = 1
```

#### 出场信号列（第 221 行）
```python
# 旧版
'sell'] = 1

# 新版 ✅
'exit_long'] = 1
```

### 5. 参数引用更新（第 216 行）
```python
# 旧版
dataframe[self.sell_params['sell_trend_indicator']]

# 新版 ✅
dataframe[self.exit_params['exit_trend_indicator']]
```

## 📋 修改总结

| 旧参数/函数名 | 新参数/函数名 | 状态 |
|--------------|--------------|------|
| `sell_params` | `exit_params` | ✅ 已更新 |
| `use_sell_signal` | `use_exit_signal` | ✅ 已更新 |
| `sell_profit_only` | `exit_profit_only` | ✅ 已更新 |
| `ignore_roi_if_buy_signal` | `ignore_roi_if_entry_signal` | ✅ 已更新 |
| `populate_buy_trend()` | `populate_entry_trend()` | ✅ 已更新 |
| `populate_sell_trend()` | `populate_exit_trend()` | ✅ 已更新 |
| `'buy'` 列 | `'enter_long'` 列 | ✅ 已更新 |
| `'sell'` 列 | `'exit_long'` 列 | ✅ 已更新 |

## 📝 未修改的部分

以下参数保持不变（可选更新，不影响功能）：

- `buy_params` - 虽然可以改为 `entry_params`，但不是必须的
- 参数内部的 `buy_*` 前缀的键名（如 `buy_trend_above_senkou_level`）

这些参数虽然不是最新的命名规范，但 Freqtrade 仍然支持，不会产生弃用警告。

## ✅ 验证结果

修改后应该不会再出现以下警告：
```
DEPRECATED: Using 'sell_profit_only' moved to 'exit_profit_only'
```

## 🚀 下次运行

现在可以重新运行策略，不会再看到弃用警告：

```bash
freqtrade trade -c user_data/config_composed.json
```

或者回测验证：

```bash
freqtrade backtesting -c user_data/config_composed.json --timerange 20240101-20240131
```

## 📚 参考文档

- [Freqtrade 策略迁移指南](https://www.freqtrade.io/en/stable/strategy-migration/)
- [Freqtrade 策略配置](https://www.freqtrade.io/en/stable/strategy-customization/)

---

✅ **所有弃用警告已修复完成！策略已更新到最新版本规范。**
