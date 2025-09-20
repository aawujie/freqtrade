from datetime import datetime
from math import exp
from pandas import DataFrame
from freqtrade.constants import Config
from freqtrade.optimize.hyperopt import IHyperOptLoss


# ========================================
# 双均线策略优化配置常量
# ========================================

# 目标交易次数范围
TARGET_TRADES_MIN = 50    # 最少交易次数
TARGET_TRADES_MAX = 300   # 最多交易次数
TARGET_TRADES_OPTIMAL = 150  # 最优交易次数

# 预期最大利润
EXPECTED_MAX_PROFIT = 2.0  # 预期总利润至少2.0

# 最大接受的平均持仓时间（分钟）
MAX_ACCEPTED_TRADE_DURATION = 720  # 12小时

# 目标胜率范围
TARGET_WIN_RATE_MIN = 0.35  # 最少胜率35%
TARGET_WIN_RATE_MAX = 0.65  # 最多胜率65%
TARGET_WIN_RATE_OPTIMAL = 0.50  # 最优胜率50%

# 最大回撤限制
MAX_ACCEPTED_DRAWDOWN = 0.15  # 最大接受回撤15%

# 参数合理性权重
REASONABLE_PARAMS_WEIGHT = 0.1  # 参数合理性权重


class DoubleMAHyperOptLoss(IHyperOptLoss):
    """
    双均线策略专用Hyperopt Loss函数

    优化目标：
    1. 平衡利润和风险
    2. 确保交易频率合理
    3. 保证参数组合的合理性
    4. 避免过拟合

    评分标准：
    - 利润：越高越好
    - 胜率：40-60%最优
    - 回撤：越小越好
    - 交易频率：每月10-30笔最优
    - 参数合理性：快慢线周期比例合理
    """

    @staticmethod
    def hyperopt_loss_function(
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: Config,
        processed: dict[str, DataFrame],
        *args,
        **kwargs,
    ) -> float:
        """
        双均线策略的自定义损失函数

        返回值越小，策略表现越好
        """

        # ========================================
        # 1. 基础指标计算
        # ========================================

        # 计算时间范围（天数）
        days = (max_date - min_date).days
        if days == 0:
            days = 1  # 避免除零错误

        # 基础交易指标
        total_profit = results['profit_ratio'].sum() if len(results) > 0 else 0
        win_rate = (results['profit_ratio'] > 0).sum() / len(results) if len(results) > 0 else 0
        avg_profit = results['profit_ratio'].mean() if len(results) > 0 else 0

        # 回撤相关指标 - 从策略统计信息中获取
        # 注意：在Hyperopt中，max_drawdown需要通过其他方式获取
        # 这里使用近似方法：基于交易利润计算
        if len(results) > 0:
            # 计算累积利润
            cumulative_profit = results['profit_ratio'].cumsum()
            # 计算最大回撤（从最高点到最低点的最大跌幅）
            peak = cumulative_profit.expanding().max()
            drawdown = cumulative_profit - peak
            max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0
            avg_drawdown = abs(drawdown.mean()) if len(drawdown) > 0 else 0
        else:
            max_drawdown = 0
            avg_drawdown = 0

        # 交易频率指标
        trades_per_day = trade_count / days
        trades_per_month = trades_per_day * 30

        # 持仓时间指标
        avg_trade_duration = results['trade_duration'].mean() if len(results) > 0 else 0

        # ========================================
        # 2. 各指标损失计算
        # ========================================

        # 2.1 利润损失
        if total_profit > 0:
            # 利润为正时，鼓励更高利润
            profit_loss = max(0, 1 - total_profit / EXPECTED_MAX_PROFIT)
        else:
            # 利润为负时，给予重罚
            profit_loss = 2 + abs(total_profit)

        # 2.2 胜率损失（目标40-60%胜率）
        if win_rate < TARGET_WIN_RATE_MIN:
            win_rate_loss = (TARGET_WIN_RATE_MIN - win_rate) * 2
        elif win_rate > TARGET_WIN_RATE_MAX:
            win_rate_loss = (win_rate - TARGET_WIN_RATE_MAX) * 1.5
        else:
            # 在最优范围内，给与奖励
            distance_from_optimal = abs(win_rate - TARGET_WIN_RATE_OPTIMAL)
            win_rate_loss = distance_from_optimal * 0.5

        # 2.3 回撤损失
        if max_drawdown > MAX_ACCEPTED_DRAWDOWN:
            drawdown_loss = (max_drawdown - MAX_ACCEPTED_DRAWDOWN) * 3
        else:
            drawdown_loss = max_drawdown * 2

        # 2.4 交易频率损失（目标每月10-30笔）
        if trades_per_month < 10:
            freq_loss = (10 - trades_per_month) * 0.1
        elif trades_per_month > 30:
            freq_loss = (trades_per_month - 30) * 0.05
        else:
            freq_loss = 0

        # 2.5 持仓时间损失（避免持仓过长）
        if avg_trade_duration > MAX_ACCEPTED_TRADE_DURATION:
            duration_loss = (avg_trade_duration - MAX_ACCEPTED_TRADE_DURATION) / 1000
        else:
            duration_loss = 0

        # 2.6 交易次数损失（确保有足够样本）
        if trade_count < TARGET_TRADES_MIN:
            trade_count_loss = (TARGET_TRADES_MIN - trade_count) * 0.01
        elif trade_count > TARGET_TRADES_MAX:
            trade_count_loss = (trade_count - TARGET_TRADES_MAX) * 0.005
        else:
            trade_count_loss = 0

        # 2.7 参数合理性损失
        params_reasonable_loss = DoubleMAHyperOptLoss._calculate_params_reasonable_loss(config)

        # ========================================
        # 3. 综合评分
        # ========================================

        # 各损失项的权重分配
        weights = {
            'profit': 0.25,      # 利润权重25%
            'win_rate': 0.20,    # 胜率权重20%
            'drawdown': 0.20,    # 回撤权重20%
            'frequency': 0.10,   # 频率权重10%
            'duration': 0.10,    # 持仓时间权重10%
            'trade_count': 0.10, # 交易次数权重10%
            'params': REASONABLE_PARAMS_WEIGHT  # 参数合理性权重
        }

        total_loss = (
            profit_loss * weights['profit'] +
            win_rate_loss * weights['win_rate'] +
            drawdown_loss * weights['drawdown'] +
            freq_loss * weights['frequency'] +
            duration_loss * weights['duration'] +
            trade_count_loss * weights['trade_count'] +
            params_reasonable_loss * weights['params']
        )

        # 调试信息输出（可选）
        if kwargs.get('debug', False):
            DoubleMAHyperOptLoss._print_debug_info(
                total_profit, win_rate, max_drawdown, trade_count,
                trades_per_month, avg_trade_duration, total_loss,
                profit_loss, win_rate_loss, drawdown_loss,
                freq_loss, duration_loss, trade_count_loss, params_reasonable_loss
            )

        return total_loss

    @staticmethod
    def _calculate_params_reasonable_loss(config: Config) -> float:
        """
        计算参数合理性损失
        确保快慢线周期比例合理，避免过拟合
        """
        try:
            # 获取当前的参数值
            strategy_config = config.get('strategy', {})
            fast_period = strategy_config.get('fast_ma_period', 10)
            slow_period = strategy_config.get('slow_ma_period', 30)
            trend_period = strategy_config.get('trend_filter_period', 100)

            # 计算参数合理性评分
            params_loss = 0

            # 1. 快慢线周期比例合理性（快线应明显小于慢线）
            period_ratio = fast_period / slow_period
            if period_ratio > 0.8:
                params_loss += (period_ratio - 0.8) * 2  # 快慢线差距太小
            elif period_ratio < 0.1:
                params_loss += (0.1 - period_ratio) * 1  # 快慢线差距太大

            # 2. 趋势过滤周期应大于慢线周期
            if trend_period <= slow_period:
                params_loss += (slow_period - trend_period + 1) * 0.01

            # 3. 避免极端参数值
            if fast_period < 3 or fast_period > 100:
                params_loss += 0.5
            if slow_period < 10 or slow_period > 200:
                params_loss += 0.5
            if trend_period < 20 or trend_period > 500:
                params_loss += 0.5

            return params_loss

        except Exception:
            # 如果无法获取参数，返回默认值
            return 0.1

    @staticmethod
    def _print_debug_info(total_profit, win_rate, max_drawdown, trade_count,
                         trades_per_month, avg_trade_duration, total_loss,
                         profit_loss, win_rate_loss, drawdown_loss,
                         freq_loss, duration_loss, trade_count_loss, params_reasonable_loss):
        """
        打印调试信息
        """
        print(f"""
        === 双均线策略优化调试信息 ===
        基础指标:
          总利润: {total_profit:.4f}
          胜率: {win_rate:.2%}
          最大回撤: {max_drawdown:.2%}
          交易次数: {trade_count}
          月均交易: {trades_per_month:.1f}
          平均持仓: {avg_trade_duration:.0f}分钟

        各项损失:
          利润损失: {profit_loss:.4f}
          胜率损失: {win_rate_loss:.4f}
          回撤损失: {drawdown_loss:.4f}
          频率损失: {freq_loss:.4f}
          持仓损失: {duration_loss:.4f}
          交易数损失: {trade_count_loss:.4f}
          参数合理性损失: {params_reasonable_loss:.4f}

        总损失: {total_loss:.6f}
        ============================
        """)
