# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Optional, Union

from freqtrade.strategy import (
    IStrategy,
    Trade,
    Order,
    PairLocks,
    informative,  # @informative decorator
    # Hyperopt Parameters
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    RealParameter,
    # timeframe helpers
    timeframe_to_minutes,
    timeframe_to_next_date,
    timeframe_to_prev_date,
    # Strategy helper functions
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
from technical import qtpylib


class DoubleMAStrategy(IStrategy):
    """
    双均线交叉策略 (Double Moving Average Crossover Strategy)

    交易逻辑：
    - 买入信号：快线上穿慢线（金叉）
    - 卖出信号：快线下穿慢线（死叉）

    可优化参数：
    - fast_ma_period: 快线周期 (5-50)
    - slow_ma_period: 慢线周期 (20-100)
    - ma_type: 均线类型 (SMA/EMA/WMA)
    """

    # Strategy interface version
    INTERFACE_VERSION = 3

    # 是否允许做空
    can_short: bool = False

    # 最小收益目标
    minimal_roi = {
        "1440": 0.02,   # 24小时内获利2%
        "720": 0.03,    # 12小时内获利3%
        "360": 0.04,    # 6小时内获利4%
        "180": 0.05,    # 3小时内获利5%
        "0": 0.06       # 立即获利6%
    }

    # 止损设置
    stoploss = -0.08

    # 追踪止损
    trailing_stop = False
    trailing_only_offset_is_reached = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.0

    # 最佳时间周期
    timeframe = "1h"

    # 只在新的K线产生信号
    process_only_new_candles = True

    # 退出信号设置
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # 启动所需的最小K线数量
    startup_candle_count: int = 50

    # ========================================
    # 可优化参数定义
    # ========================================

    # 均线周期参数
    fast_ma_period = IntParameter(
        low=5, high=50, default=10,
        space="buy", optimize=True, load=True
    )
    slow_ma_period = IntParameter(
        low=20, high=100, default=30,
        space="buy", optimize=True, load=True
    )

    # 均线类型选择
    ma_type = CategoricalParameter(
        ["SMA", "EMA", "WMA"],  # SMA:简单移动平均, EMA:指数移动平均, WMA:加权移动平均
        default="EMA",
        space="buy",
        optimize=True,
        load=True
    )

    # 信号确认参数
    min_volume_multiplier = DecimalParameter(
        low=0.5, high=3.0, default=1.0,
        space="buy", optimize=True, load=True
    )

    # 趋势过滤参数
    trend_filter_period = IntParameter(
        low=50, high=200, default=100,
        space="buy", optimize=True, load=True
    )

    # ========================================
    # 策略方法
    # ========================================

    def informative_pairs(self):
        """
        定义额外的参考数据
        这里可以添加更大时间周期的数据作为趋势参考
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算所有需要的指标
        """

        # 根据选择的均线类型计算快慢线
        if self.ma_type.value == "SMA":
            # 简单移动平均线
            dataframe['fast_ma'] = ta.SMA(dataframe, timeperiod=self.fast_ma_period.value)
            dataframe['slow_ma'] = ta.SMA(dataframe, timeperiod=self.slow_ma_period.value)
        elif self.ma_type.value == "EMA":
            # 指数移动平均线
            dataframe['fast_ma'] = ta.EMA(dataframe, timeperiod=self.fast_ma_period.value)
            dataframe['slow_ma'] = ta.EMA(dataframe, timeperiod=self.slow_ma_period.value)
        elif self.ma_type.value == "WMA":
            # 加权移动平均线
            dataframe['fast_ma'] = ta.WMA(dataframe, timeperiod=self.fast_ma_period.value)
            dataframe['slow_ma'] = ta.WMA(dataframe, timeperiod=self.slow_ma_period.value)

        # 趋势过滤指标 - 使用更大周期的EMA判断整体趋势
        dataframe['trend_filter'] = ta.EMA(dataframe, timeperiod=self.trend_filter_period.value)

        # 成交量指标
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)

        # 计算均线交叉信号
        dataframe['ma_cross_up'] = qtpylib.crossed_above(dataframe['fast_ma'], dataframe['slow_ma'])
        dataframe['ma_cross_down'] = qtpylib.crossed_below(dataframe['fast_ma'], dataframe['slow_ma'])

        # 计算趋势方向 (快线相对于慢线的斜率)
        dataframe['fast_ma_slope'] = dataframe['fast_ma'] - dataframe['fast_ma'].shift(1)
        dataframe['slow_ma_slope'] = dataframe['slow_ma'] - dataframe['slow_ma'].shift(1)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        生成买入信号
        买入条件：
        1. 金叉信号（快线上穿慢线）
        2. 价格在快线上方（确认上涨趋势）
        3. 成交量放大（确认信号强度）
        4. 整体趋势向上（可选）
        """

        dataframe.loc[
            (
                # 主要信号：金叉
                dataframe['ma_cross_up']

                # 价格确认：当前价格高于快线
                & (dataframe['close'] > dataframe['fast_ma'])

                # 成交量确认：成交量大于平均水平
                & (dataframe['volume'] > dataframe['volume_sma'] * self.min_volume_multiplier.value)

                # 可选：整体趋势向上（价格高于趋势线）
                & (dataframe['close'] > dataframe['trend_filter'])

                # 确保成交量不为0
                & (dataframe['volume'] > 0)
            ),
            'enter_long'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        生成卖出信号
        卖出条件：
        1. 死叉信号（快线下穿慢线）
        2. 或价格跌破慢线
        """

        dataframe.loc[
            (
                # 主要信号：死叉
                dataframe['ma_cross_down']

                # 或者价格跌破慢线
                | (dataframe['close'] < dataframe['slow_ma'])
            ),
            'exit_long'
        ] = 1

        return dataframe

    # ========================================
    # 可选：自定义方法
    # ========================================

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                          rate: float, time_in_force: str, current_time: datetime,
                          entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """
        可选：确认交易进入
        可以在这里添加额外的交易确认逻辑
        """
        return True

    def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str,
                         amount: float, rate: float, time_in_force: str,
                         exit_reason: str, current_time: datetime, **kwargs) -> bool:
        """
        可选：确认交易退出
        可以在这里添加额外的退出确认逻辑
        """
        return True

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str],
                 side: str, **kwargs) -> float:
        """
        可选：自定义杠杆设置
        """
        return 1.0  # 使用1倍杠杆（现货交易）

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                           proposed_stake: float, min_stake: float, max_stake: float,
                           leverage: float, entry_tag: Optional[str], side: str, **kwargs) -> float:
        """
        可选：自定义仓位大小
        """
        return proposed_stake

    # ========================================
    # 绘图配置（可选）
    # ========================================

    plot_config = {
        "main_plot": {
            "fast_ma": {"color": "blue"},
            "slow_ma": {"color": "red"},
            "trend_filter": {"color": "green"},
        },
        "subplots": {
            "Volume": {
                "volume": {"color": "purple"},
                "volume_sma": {"color": "orange"},
            }
        }
    }
