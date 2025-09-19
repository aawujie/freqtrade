#!/usr/bin/env python3
"""
Feather文件预览工具
用于查看Freqtrade数据文件的内容
"""

import pandas as pd
import sys
import os
from pathlib import Path

def preview_feather_file(file_path):
    """预览.feather文件内容"""
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return

        # 读取文件
        df = pd.read_feather(file_path)

        # 基本信息
        print(f"📊 {os.path.basename(file_path)} 数据预览")
        print("=" * 60)
        print(f"📈 数据行数: {len(df):,}")
        print(f"📊 数据列数: {len(df.columns)}")
        print(f"📅 时间范围: {df['date'].min()} 到 {df['date'].max()}")
        print(f"💾 文件大小: {os.path.getsize(file_path) / 1024 / 1024:.2f} MB")
        print()

        # 列信息
        print("📋 数据列:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        print()

        # 前5行数据
        print("🔍 前5行数据:")
        print(df.head().to_string(index=False))
        print()

        # 后5行数据
        print("🔍 后5行数据:")
        print(df.tail().to_string(index=False))
        print()

        # 基本统计
        if 'close' in df.columns:
            print("📊 收盘价统计:")
            print(f"  最高价: ${df['close'].max():,.2f}")
            print(f"  最低价: ${df['close'].min():,.2f}")
            print(f"  平均价: ${df['close'].mean():,.2f}")
            print(f"  最新价: ${df['close'].iloc[-1]:,.2f}")

    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")

def main():
    if len(sys.argv) < 2:
        print("用法: python preview_feather.py <feather文件路径>")
        print("\n示例:")
        print("  python preview_feather.py user_data/data/binance/futures/BTC_USDT_USDT-5m-futures.feather")
        return

    file_path = sys.argv[1]
    preview_feather_file(file_path)

if __name__ == "__main__":
    main()
