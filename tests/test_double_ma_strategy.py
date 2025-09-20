#!/usr/bin/env python3
"""
双均线策略测试脚本
用于验证策略的基本功能和参数优化
"""

import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from freqtrade.strategy import IStrategy
from freqtrade.data import load_data
from freqtrade.resolvers import StrategyResolver
from freqtrade.configuration import Configuration
from pandas import DataFrame
import pandas as pd


def test_strategy_basic_functionality():
    """
    测试策略的基本功能
    """
    print("=== 测试双均线策略基本功能 ===\n")

    try:
        # 加载策略
        config = Configuration.from_files([str(project_root / "user_data" / "config_double_ma.json")])
        strategy = StrategyResolver.load_strategy(config)

        print(f"✅ 策略加载成功: {strategy.__class__.__name__}")
        print(f"   - 时间周期: {strategy.timeframe}")
        print(f"   - 允许做空: {strategy.can_short}")
        print(f"   - 止损设置: {strategy.stoploss}")
        print(f"   - 最小收益目标: {strategy.minimal_roi}")

        # 测试参数配置
        print("\n📊 可优化参数:")
        print(f"   - 快线周期: {strategy.fast_ma_period.value}")
        print(f"   - 慢线周期: {strategy.slow_ma_period.value}")
        print(f"   - 均线类型: {strategy.ma_type.value}")
        print(f"   - 成交量倍数: {strategy.min_volume_multiplier.value}")
        print(f"   - 趋势过滤周期: {strategy.trend_filter_period.value}")

        return True

    except Exception as e:
        print(f"❌ 策略测试失败: {e}")
        return False


def test_hyperopt_loss():
    """
    测试Hyperopt Loss函数
    """
    print("\n=== 测试Hyperopt Loss函数 ===\n")

    try:
        from user_data.hyperopts.DoubleMAHyperOptLoss import DoubleMAHyperOptLoss

        # 创建模拟的交易结果数据
        mock_results = DataFrame({
            'profit_ratio': [0.02, -0.01, 0.03, 0.01, -0.005, 0.025],
            'trade_duration': [120, 180, 90, 240, 60, 150],
            'max_drawdown': [0.05, 0.08, 0.03, 0.06, 0.04, 0.07]
        })

        # 测试Loss函数
        loss_value = DoubleMAHyperOptLoss.hyperopt_loss_function(
            results=mock_results,
            trade_count=6,
            min_date=pd.Timestamp('2024-01-01'),
            max_date=pd.Timestamp('2024-01-10'),
            config={},
            processed={}
        )

        print(f"✅ Loss函数测试成功")
        print(".6f")
        print(".4f")
        print(".2%")
        print(".2%")

        return True

    except Exception as e:
        print(f"❌ Loss函数测试失败: {e}")
        return False


def test_data_loading():
    """
    测试数据加载功能
    """
    print("\n=== 测试数据加载功能 ===\n")

    try:
        # 检查是否有测试数据
        data_dir = project_root / "user_data" / "data"
        if not data_dir.exists():
            print("⚠️  未找到数据目录，请先下载测试数据")
            return False

        # 查找可用的数据文件
        data_files = list(data_dir.glob("**/*.feather"))
        if not data_files:
            print("⚠️  未找到数据文件，请先下载测试数据")
            return False

        print(f"✅ 找到 {len(data_files)} 个数据文件")
        for file_path in data_files[:3]:  # 只显示前3个
            print(f"   - {file_path.name}")

        return True

    except Exception as e:
        print(f"❌ 数据加载测试失败: {e}")
        return False


def main():
    """
    主测试函数
    """
    print("🚀 开始测试双均线交易策略\n")

    tests = [
        ("策略基本功能", test_strategy_basic_functionality),
        ("Hyperopt Loss函数", test_hyperopt_loss),
        ("数据加载功能", test_data_loading),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"正在测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - 通过")
        else:
            print(f"❌ {test_name} - 失败")

    print(f"\n📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！策略准备就绪。")
    else:
        print("⚠️  部分测试失败，请检查配置。")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
