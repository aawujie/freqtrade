# Freqtrade 知识点笔记

## 📚 SQLite URI 格式详解

### 基本格式
```
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

### 格式分解
| 部分 | 说明 | 示例 |
|------|------|------|
| `sqlite://` | 协议标识符 | 表示这是 SQLite 数据库 |
| `///` | 路径分隔符 | 三个斜杠表示绝对路径 |
| `/freqtrade/user_data/tradesv3.dryrun.sqlite` | 实际文件路径 | 容器内的绝对路径 |

### 路径格式对比

#### 1. 相对路径格式（不推荐）
```bash
sqlite:///tradesv3.dryrun.sqlite
```

#### 2. 绝对路径格式（推荐）
```bash
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

#### 3. 本地文件系统路径
```bash
/Users/apple/code/freqtrade/user_data/tradesv3.dryrun.sqlite
```

### 容器内路径映射

| 容器内路径 | 本地路径 | 说明 |
|------------|----------|------|
| `/freqtrade/user_data/` | `/Users/apple/code/freqtrade/user_data/` | 用户数据目录 |
| `/freqtrade/user_data/tradesv3.dryrun.sqlite` | `/Users/apple/code/freqtrade/user_data/tradesv3.dryrun.sqlite` | 模拟交易数据库 |
| `/freqtrade/user_data/tradesv3.sqlite` | `/Users/apple/code/freqtrade/user_data/tradesv3.sqlite` | 实盘交易数据库 |

### SQLite 文件类型说明

| 文件扩展名 | 说明 | 作用 |
|------------|------|------|
| `.sqlite` | 主数据库文件 | 存储实际数据 |
| `.sqlite-shm` | 共享内存文件 | 多进程访问时的共享内存 |
| `.sqlite-wal` | 预写日志文件 | 事务日志，提高性能 |

### 实际应用命令

#### 查看模拟交易记录
```bash
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
```

#### 查看实盘交易记录
```bash
freqtrade show-trades \
  --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
```

### 记忆技巧
```
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
│       │  │
│       │  └─ 容器内绝对路径
│       └─ 三个斜杠 = 绝对路径
└─ SQLite 协议
```

### 为什么使用这种格式？

1. **协议标识**：`sqlite://` 告诉程序这是 SQLite 数据库
2. **绝对路径**：`///` 确保路径从根目录开始
3. **容器兼容**：在 Docker 容器内使用绝对路径
4. **跨平台**：URI 格式在不同操作系统间保持一致

---

## 🔧 常用命令速查

### 数据库相关命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `show-trades` | 查看交易记录 | `freqtrade show-trades --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite` |
| `test-pairlist` | 测试交易对列表 | `freqtrade test-pairlist` |
| `list-strategies` | 列出所有策略 | `freqtrade list-strategies` |

### 配置相关命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `show-config` | 显示当前配置 | `freqtrade show-config` |
| `test-pairlist` | 验证交易对配置 | `freqtrade test-pairlist` |

---

## 📝 重要提醒

### 数据库选择
- **模拟交易模式** (`dry_run: true`) → 使用 `tradesv3.dryrun.sqlite`
- **实盘交易模式** (`dry_run: false`) → 使用 `tradesv3.sqlite`

### 路径格式
- 容器内使用：`sqlite:////freqtrade/user_data/...`
- 本地使用：`sqlite:////Users/username/path/...`
- 相对路径：`sqlite:///filename.sqlite`（不推荐）

### 安全注意事项
- 不要将数据库文件提交到版本控制
- 定期备份重要的交易数据
- 注意数据库文件的权限设置

---

## 🎯 快速参考

### 常用数据库路径
```bash
# 模拟交易数据库
sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite

# 实盘交易数据库
sqlite:////freqtrade/user_data/tradesv3.sqlite

# 本地数据库（示例）
sqlite:////Users/username/freqtrade/user_data/tradesv3.sqlite
```

### 便捷脚本
```bash
# 使用便捷脚本查看交易记录
./show-trades.sh
```

---

**最后更新**: 2025-09-17  
**版本**: 1.0  
**作者**: Freqtrade 学习笔记
