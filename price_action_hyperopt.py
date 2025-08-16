#!/usr/bin/env python3
"""
Al Brooks价格行为策略超参数优化脚本
专注于核心价格行为参数的优化
"""

import os
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

def run_hyperopt_price_action():
    """运行价格行为策略超参数优化"""
    
    print("🎯 开始Al Brooks价格行为策略超参数优化")
    print("专注优化: 趋势识别、突破确认、回踩深度、楔形参数")
    
    # 价格行为策略超参数优化命令
    hyperopt_command = f"""python -m freqtrade hyperopt \\
        --strategy PriceActionStrategy \\
        --timeframe 5m \\
        --timerange 20240101- \\
        --pairs BTC/USDT ETH/USDT BNB/USDT SOL/USDT XRP/USDT \\
        --epochs 200 \\
        --spaces buy \\
        --hyperopt-loss SortinoHyperOptLoss \\
        --starting-balance 10000 \\
        --trading-mode futures \\
        --enable-protections \\
        --dry-run-wallet 10000 \\
        --min-trades 50 \\
        --random-state 42"""
    
    print(f"\n优化目标: Sortino比率(下行风险调整收益)")
    print(f"优化空间: 价格行为核心参数")
    print(f"命令: {hyperopt_command}")
    print("\n⏳ 正在运行优化 (预计需要较长时间，Al Brooks策略复杂度较高)...")
    
    try:
        result = subprocess.run(hyperopt_command, shell=True, check=True, 
                              capture_output=True, text=True, cwd="/home/user/webapp")
        print("\n✅ 价格行为策略超参数优化完成!")
        print("优化结果:")
        print(result.stdout)
        
        # 显示最佳结果
        print("\n📊 显示最佳价格行为策略参数:")
        show_command = "python -m freqtrade hyperopt-show -n 5"  # 显示前5个最佳结果
        result2 = subprocess.run(show_command, shell=True, check=True,
                               capture_output=True, text=True, cwd="/home/user/webapp")
        print(result2.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 优化失败: {e}")
        print(f"错误信息: {e.stderr}")
        return False

def create_optimized_price_action_strategy():
    """根据优化结果创建优化后的价格行为策略"""
    
    print("\n🔧 创建优化后的Al Brooks价格行为策略...")
    
    # 这里创建一个优化后的策略模板
    optimized_strategy = '''# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# Al Brooks价格行为策略 - 超参数优化版本

import numpy as np
import pandas as pd
from datetime import datetime
from pandas import DataFrame
from typing import Optional
from enum import Enum

from freqtrade.strategy import IStrategy
import talib.abstract as ta
from technical import qtpylib

class MarketState(Enum):
    """Always In市场状态枚举"""
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"  
    RANGE = "range"

class OptimizedPriceActionStrategy(IStrategy):
    """
    基于超参数优化的Al Brooks价格行为策略
    
    优化后的参数基于历史回测结果，针对以下方面进行了调优:
    - Always In状态识别精度
    - 突破-回踩时机把握
    - 楔形反转识别准确性
    - 风险调整收益率最大化
    """
    
    INTERFACE_VERSION = 3
    can_short: bool = True
    
    # 基于优化结果的固定参数 (示例值，需根据实际hyperopt结果调整)
    minimal_roi = {
        "0": 0.12,
        "60": 0.06,
        "120": 0.03,
        "240": 0.01
    }
    
    stoploss = -0.025  # 优化后的止损
    timeframe = "5m"
    
    # === 优化后的价格行为参数 ===
    # (以下参数值为示例，实际使用时需要根据hyperopt结果调整)
    
    # ATR和趋势强度
    atr_period = 14
    trend_strength_atr = 1.7  # 优化后的趋势强度阈值
    trend_follow_atr = 2.3    # 优化后的跟随确认阈值
    
    # 突破回踩参数
    breakout_lookback = 12    # 优化后的突破回看期
    pullback_depth = 0.42     # 优化后的回踩深度
    pullback_bars = 3         # 优化后的回踩K线数
    
    # 楔形识别参数
    wedge_bars = 8            # 优化后的楔形识别期
    divergence_threshold = 0.25  # 优化后的背离阈值
    
    # 过滤参数
    range_overlap_threshold = 0.68  # 优化后的震荡识别阈值
    risk_per_trade = 0.006    # 优化后的单笔风险
    
    startup_candle_count: int = 200
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """使用优化后参数的指标计算"""
        
        # 基础指标
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period)
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # K线分析
        dataframe['body_size'] = abs(dataframe['close'] - dataframe['open'])
        dataframe['total_range'] = dataframe['high'] - dataframe['low']
        dataframe['body_ratio'] = dataframe['body_size'] / (dataframe['total_range'] + 0.0001)
        
        # 强信号棒(使用优化后的标准)
        dataframe['strong_bull_bar'] = (
            (dataframe['close'] > dataframe['open']) & 
            (dataframe['body_ratio'] > 0.65) &  # 优化后的实体比例
            (dataframe['body_size'] > dataframe['atr'] * 0.8)  # 优化后的实体大小要求
        )
        
        dataframe['strong_bear_bar'] = (
            (dataframe['close'] < dataframe['open']) & 
            (dataframe['body_ratio'] > 0.65) &
            (dataframe['body_size'] > dataframe['atr'] * 0.8)
        )
        
        # Always In状态(使用优化后的参数)
        dataframe['rolling_high'] = dataframe['high'].rolling(window=self.breakout_lookback).max()
        dataframe['rolling_low'] = dataframe['low'].rolling(window=self.breakout_lookback).min()
        
        # 简化的状态判断(实际应使用完整逻辑)
        dataframe['market_state'] = 0
        
        # 强突破识别(使用优化后的阈值)
        strong_breakout_up = (
            (dataframe['close'] > dataframe['rolling_high'].shift(1)) &
            (dataframe['close'] - dataframe['rolling_high'].shift(1) >= 
             dataframe['atr'] * self.trend_strength_atr) &
            dataframe['strong_bull_bar']
        )
        
        strong_breakout_down = (
            (dataframe['close'] < dataframe['rolling_low'].shift(1)) &
            (dataframe['rolling_low'].shift(1) - dataframe['close'] >= 
             dataframe['atr'] * self.trend_strength_atr) &
            dataframe['strong_bear_bar']
        )
        
        # 状态赋值
        dataframe.loc[strong_breakout_up, 'market_state'] = 1
        dataframe.loc[strong_breakout_down, 'market_state'] = -1
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """使用优化后参数的入场逻辑"""
        
        # 多头入场(使用优化后的条件组合)
        dataframe.loc[
            (
                # Always In多头状态
                (dataframe['market_state'] == 1) &
                
                # 强信号棒
                dataframe['strong_bull_bar'] &
                
                # 价格动能(使用优化后的标准)
                (dataframe['close'] > dataframe['ema_20']) &
                (dataframe['close'] > dataframe['open'] * 1.002) &  # 优化后的强度要求
                
                # RSI过滤(使用优化后的范围)
                (dataframe['rsi'] > 35) &
                (dataframe['rsi'] < 78) &
                
                # 基础条件
                (dataframe['volume'] > 0)
            ),
            "enter_long",
        ] = 1
        
        # 空头入场
        dataframe.loc[
            (
                (dataframe['market_state'] == -1) &
                dataframe['strong_bear_bar'] &
                (dataframe['close'] < dataframe['ema_20']) &
                (dataframe['close'] < dataframe['open'] * 0.998) &
                (dataframe['rsi'] < 65) &
                (dataframe['rsi'] > 22) &
                (dataframe['volume'] > 0)
            ),
            "enter_short",
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """使用优化后参数的出场逻辑"""
        
        # 多头出场
        dataframe.loc[
            (
                # 状态转换
                (dataframe['market_state'] == -1) |
                
                # 弱势信号
                (dataframe['strong_bear_bar'] & 
                 (dataframe['close'] < dataframe['ema_20'])) |
                
                # RSI极值
                (dataframe['rsi'] > 82)
            ) &
            (dataframe['volume'] > 0),
            "exit_long",
        ] = 1
        
        # 空头出场
        dataframe.loc[
            (
                (dataframe['market_state'] == 1) |
                (dataframe['strong_bull_bar'] & 
                 (dataframe['close'] > dataframe['ema_20'])) |
                (dataframe['rsi'] < 18)
            ) &
            (dataframe['volume'] > 0),
            "exit_short",
        ] = 1
        
        return dataframe
'''
    
    # 写入优化后的策略文件
    with open("/home/user/webapp/user_data/strategies/OptimizedPriceActionStrategy.py", "w", encoding="utf-8") as f:
        f.write(optimized_strategy)
    
    print("✅ 优化后的价格行为策略已保存为: OptimizedPriceActionStrategy.py")
    print("📝 注意: 请根据实际的hyperopt结果手动调整所有参数值")

def analyze_optimization_results():
    """分析优化结果并提供洞察"""
    
    analysis = """
    
    🔬 Al Brooks价格行为策略优化分析框架:
    ================================================
    
    📊 关键参数优化方向:
    
    1. trend_strength_atr (趋势强度阈值):
       • 过小: 假突破增加，噪音过多
       • 过大: 错失早期趋势机会
       • 最优值通常在1.5-2.0之间
    
    2. pullback_depth (回踩深度):
       • Brooks理论: 健康回踩不超过50%
       • 过浅: 入场机会减少
       • 过深: 可能是趋势结束信号
       • 建议范围: 0.3-0.6
    
    3. wedge_bars (楔形识别期):
       • 影响三推结构识别准确性
       • 过短: 识别不充分
       • 过长: 信号滞后
       • 建议范围: 8-15
    
    4. range_overlap_threshold (震荡识别):
       • 决定是否暂停趋势策略
       • 过低: 震荡市仍执行趋势策略(危险)
       • 过高: 错失弱趋势机会
       • 建议范围: 0.6-0.8
    
    🎯 优化目标权衡:
    
    • Sortino比率: 重点关注下行风险
    • 最大回撤: Always In理念的风险控制
    • 交易频次: 避免过度交易
    • 胜率vs盈亏比: Brooks强调的核心权衡
    
    💡 市场适应性:
    
    • 不同品种可能需要不同参数
    • 牛市vs熊市的参数调整
    • 波动率环境的影响
    • 时间周期的影响
    
    🔧 后续优化方向:
    
    1. 动态参数: 根据市场状态自适应
    2. 多品种联合优化
    3. 机器学习增强的状态识别
    4. 更精细的风险管理
    
    """
    
    print(analysis)

def main():
    """主函数"""
    print("🎯 Al Brooks价格行为策略超参数优化系统")
    
    # 检查策略文件
    strategy_path = "/home/user/webapp/user_data/strategies/PriceActionStrategy.py"
    if not os.path.exists(strategy_path):
        print(f"❌ 策略文件不存在: {strategy_path}")
        return
    
    # 分析优化理论基础
    analyze_optimization_results()
    
    # 运行优化
    if run_hyperopt_price_action():
        create_optimized_price_action_strategy()
        
        print("\n📋 价格行为策略优化完成总结:")
        print("""
        ✅ 已完成Al Brooks价格行为策略超参数优化
        ✅ 已生成优化后的策略模板
        ✅ 提供了理论分析框架
        
        📝 后续步骤:
        1. 查看hyperopt结果，获取最佳参数组合
        2. 手动更新OptimizedPriceActionStrategy.py中的所有参数
        3. 使用优化后的策略进行样本外验证
        4. 在不同市场环境中测试稳健性
        5. 考虑多品种的参数差异化
        
        🔍 查看详细结果:
        python -m freqtrade hyperopt-list
        python -m freqtrade hyperopt-show -n 1  # 显示最佳结果
        python -m freqtrade hyperopt-show -n 5  # 显示前5个结果
        
        📊 深度分析建议:
        • 关注Sortino比率最高的参数组合
        • 验证在不同时期的稳定性
        • 分析各策略模块的贡献度
        • 考虑参数的经济意义和理论基础
        
        🎯 Al Brooks理念验证:
        • Always In状态转换的准确性
        • 测量移动70%达成率验证
        • 震荡vs趋势市场的策略切换效果
        • 概率×盈亏比优化结果
        """)
    else:
        print("\n❌ 优化失败，请检查错误信息并重试")

if __name__ == "__main__":
    main()