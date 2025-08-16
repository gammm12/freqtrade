#!/usr/bin/env python3
"""
布林带回踩EMA20策略超参数优化脚本
"""

import os
import subprocess
import pandas as pd
from pathlib import Path

def run_hyperopt():
    """运行超参数优化"""
    
    print("🚀 开始布林带回踩EMA20策略超参数优化")
    
    # 超参数优化命令
    hyperopt_command = """python -m freqtrade hyperopt \
        --strategy BollingerEmaRetraceStrategy \
        --timeframe 15m \
        --timerange 20240101- \
        --pairs BTC/USDT ETH/USDT BNB/USDT ADA/USDT SOL/USDT \
        --epochs 100 \
        --spaces buy \
        --hyperopt-loss SharpeHyperOptLoss \
        --starting-balance 1000 \
        --trading-mode futures \
        --enable-protections \
        --dry-run-wallet 1000 \
        --min-trades 20"""
    
    print(f"\n命令: {hyperopt_command}")
    print("\n⏳ 正在运行优化 (预计需要几分钟)...")
    
    try:
        result = subprocess.run(hyperopt_command, shell=True, check=True, 
                              capture_output=True, text=True, cwd="/home/user/webapp")
        print("\n✅ 超参数优化完成!")
        print("优化结果:")
        print(result.stdout)
        
        # 显示最佳结果
        print("\n📊 显示最佳优化结果:")
        show_command = "python -m freqtrade hyperopt-show"
        result2 = subprocess.run(show_command, shell=True, check=True,
                               capture_output=True, text=True, cwd="/home/user/webapp")
        print(result2.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 优化失败: {e}")
        print(f"错误信息: {e.stderr}")
        return False

def create_optimized_strategy():
    """根据优化结果创建新的策略文件"""
    
    print("\n🔧 创建优化后的策略...")
    
    # 这里可以根据优化结果修改策略参数
    optimized_strategy = """# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# 基于超参数优化的布林带回踩EMA20策略

import numpy as np
import pandas as pd
from datetime import datetime
from pandas import DataFrame
from typing import Optional

from freqtrade.strategy import IStrategy
import talib.abstract as ta
from technical import qtpylib

class OptimizedBollingerEmaStrategy(IStrategy):
    \"\"\"
    优化后的布林带回踩EMA20策略
    \"\"\"
    
    INTERFACE_VERSION = 3
    can_short: bool = True
    
    # 基于优化结果的参数 (这些值应该根据实际优化结果调整)
    minimal_roi = {
        "0": 0.08,
        "15": 0.04,
        "30": 0.02,
        "60": 0.01
    }
    
    stoploss = -0.03
    timeframe = "15m"
    
    # 优化后的固定参数 (示例，实际使用时根据hyperopt结果调整)
    bb_period = 20
    bb_std = 2.1
    ema_period = 20
    retrace_candles = 4
    bb_break_strength = 0.007
    
    startup_candle_count: int = 100
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 使用优化后的参数计算指标
        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), 
            window=self.bb_period, 
            stds=self.bb_std
        )
        dataframe["bb_lowerband"] = bollinger["lower"]
        dataframe["bb_middleband"] = bollinger["mid"]
        dataframe["bb_upperband"] = bollinger["upper"]
        
        dataframe["ema20"] = ta.EMA(dataframe, timeperiod=self.ema_period)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["volume_sma"] = ta.SMA(dataframe["volume"], timeperiod=20)
        
        # 突破信号
        dataframe["bb_upper_break"] = (
            (dataframe["close"] > dataframe["bb_upperband"]) &
            (dataframe["close"].shift(1) <= dataframe["bb_upperband"].shift(1))
        )
        
        dataframe["bb_lower_break"] = (
            (dataframe["close"] < dataframe["bb_lowerband"]) &
            (dataframe["close"].shift(1) >= dataframe["bb_lowerband"].shift(1))
        )
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 使用优化后的入场逻辑
        # 这里应该根据优化结果调整条件
        
        dataframe.loc[
            (
                # 简化的做多条件 (基于优化结果调整)
                (dataframe["close"] > dataframe["ema20"]) &
                (dataframe["close"] <= dataframe["ema20"] * 1.02) &
                (dataframe["rsi"] > 45) &
                (dataframe["rsi"] < 75) &
                (dataframe["volume"] > dataframe["volume_sma"] * 0.8)
            ),
            "enter_long",
        ] = 1
        
        dataframe.loc[
            (
                # 简化的做空条件 (基于优化结果调整)
                (dataframe["close"] < dataframe["ema20"]) &
                (dataframe["close"] >= dataframe["ema20"] * 0.98) &
                (dataframe["rsi"] < 55) &
                (dataframe["rsi"] > 25) &
                (dataframe["volume"] > dataframe["volume_sma"] * 0.8)
            ),
            "enter_short",
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 出场信号
        dataframe.loc[
            (
                (dataframe["rsi"] > 80) |
                (dataframe["close"] < dataframe["ema20"] * 0.97)
            ),
            "exit_long",
        ] = 1
        
        dataframe.loc[
            (
                (dataframe["rsi"] < 20) |
                (dataframe["close"] > dataframe["ema20"] * 1.03)
            ),
            "exit_short",
        ] = 1
        
        return dataframe
"""
    
    # 写入优化后的策略文件
    with open("/home/user/webapp/user_data/strategies/OptimizedBollingerEmaStrategy.py", "w", encoding="utf-8") as f:
        f.write(optimized_strategy)
    
    print("✅ 优化后的策略已保存为: OptimizedBollingerEmaStrategy.py")
    print("📝 注意: 请根据实际的hyperopt结果手动调整参数值")

def main():
    """主函数"""
    print("🎯 布林带回踩EMA20策略超参数优化")
    
    # 检查策略文件
    strategy_path = "/home/user/webapp/user_data/strategies/BollingerEmaRetraceStrategy.py"
    if not os.path.exists(strategy_path):
        print(f"❌ 策略文件不存在: {strategy_path}")
        return
    
    # 运行优化
    if run_hyperopt():
        create_optimized_strategy()
        
        print("\n📋 优化完成总结:")
        print("""
        ✅ 已完成超参数优化
        ✅ 已生成优化后的策略模板
        
        📝 后续步骤:
        1. 查看hyperopt结果，获取最佳参数组合
        2. 手动更新OptimizedBollingerEmaStrategy.py中的参数
        3. 使用优化后的策略进行回测验证
        4. 在模拟环境中测试策略表现
        
        🔍 查看详细结果:
        python -m freqtrade hyperopt-list
        python -m freqtrade hyperopt-show -n 1  # 显示最佳结果
        """)
    else:
        print("\n❌ 优化失败，请检查错误信息并重试")

if __name__ == "__main__":
    main()