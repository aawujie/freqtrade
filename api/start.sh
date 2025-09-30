#!/bin/bash
# 启动 Freqtrade API 服务

cd "$(dirname "$0")"

echo "🚀 启动 Freqtrade API 服务..."

# 检查是否安装了依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip3 install -r requirements.txt
fi

# 启动服务
echo "✅ 服务启动在: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""

python3 main.py
