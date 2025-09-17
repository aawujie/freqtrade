#!/bin/bash

# Freqtrade 交易记录查看脚本

echo "🔍 检查交易模式..."

# 检查是否为模拟交易模式
if grep -q '"dry_run": true' user_data/config.json; then
    echo "📊 当前为模拟交易模式，查看模拟交易记录..."
    docker compose exec freqtrade freqtrade show-trades \
        --db-url sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite
else
    echo "💰 当前为实盘交易模式，查看实盘交易记录..."
    docker compose exec freqtrade freqtrade show-trades \
        --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
fi
