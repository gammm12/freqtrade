#!/usr/bin/env python3
"""
布林带回踩EMA20策略回测脚本
"""

import os
import sys
import subprocess
import pandas as pd
from pathlib import Path

def run_command(command, description):
    """执行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, cwd="/home/user/webapp")
        print("✅ 成功!")
        if result.stdout:
            print("输出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失败!")
        print("错误信息:")
        print(e.stderr)
        return False

def main():
    """主函数"""
    print("🚀 布林带回踩EMA20策略回测系统")
    
    # 1. 检查策略文件
    strategy_path = "/home/user/webapp/user_data/strategies/BollingerEmaRetraceStrategy.py"
    if not os.path.exists(strategy_path):
        print(f"❌ 策略文件不存在: {strategy_path}")
        return False
    
    print(f"✅ 策略文件存在: {strategy_path}")
    
    # 2. 下载历史数据 (最近30天的15分钟数据)
    print("\n📥 下载历史数据...")
    
    pairs = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    
    for pair in pairs:
        command = f"python -m freqtrade download-data --exchange binance --timeframes 15m --pairs {pair} --days 30 --trading-mode futures"
        success = run_command(command, f"下载 {pair} 15分钟数据 (30天)")
        
        if not success:
            print(f"⚠️  {pair} 数据下载失败，继续其他币种...")
    
    # 3. 验证策略语法
    print("\n🔍 验证策略语法...")
    command = "python -c \"from user_data.strategies.BollingerEmaRetraceStrategy import BollingerEmaRetraceStrategy; print('策略语法检查通过')\""
    success = run_command(command, "策略语法验证")
    
    if not success:
        print("❌ 策略语法验证失败，请检查代码")
        return False
    
    # 4. 运行回测
    print("\n📊 运行策略回测...")
    
    # 创建临时回测配置
    backtest_command = """python -m freqtrade backtesting \
        --strategy BollingerEmaRetraceStrategy \
        --timeframe 15m \
        --timerange 20240101- \
        --pairs BTC/USDT ETH/USDT BNB/USDT \
        --starting-balance 1000 \
        --trading-mode futures \
        --enable-protections \
        --dry-run-wallet 1000"""
    
    success = run_command(backtest_command, "执行回测分析")
    
    if success:
        print("\n🎉 回测完成!")
        
        # 5. 显示回测结果
        print("\n📈 回测结果分析:")
        result_command = "python -m freqtrade backtesting-show --strategy BollingerEmaRetraceStrategy"
        run_command(result_command, "显示回测结果")
        
    else:
        print("❌ 回测执行失败")
        
    # 6. 策略参数说明
    print("\n📋 策略参数说明:")
    print("""
    🔹 策略名称: BollingerEmaRetraceStrategy (布林带回踩EMA20策略)
    🔹 时间框架: 15分钟
    🔹 交易模式: 支持做多做空
    
    📊 技术指标:
    • 布林带 (20, 2.0): 识别价格突破
    • EMA20: 回踩支撑/阻力位
    • RSI (14): 动量确认
    • 成交量: 突破确认
    
    🎯 入场逻辑:
    • 做多: 收盘价突破布林带上轨 → 回踩EMA20附近 → 限价买入
    • 做空: 收盘价跌破布林带下轨 → 反弹至EMA20附近 → 限价卖出
    
    ⚡ 风险管理:
    • 止损: 3%
    • 追踪止损: 启用 (2%开始追踪，3%触发)
    • 最大持仓: 3个
    • 杠杆: 2倍 (保守)
    
    🔧 可优化参数:
    • bb_period: 布林带周期 (15-25)
    • bb_std: 布林带标准差 (1.8-2.5)
    • ema_period: EMA周期 (15-25)
    • retrace_candles: 回踩确认K线数 (2-8)
    """)
    
    return True

if __name__ == "__main__":
    main()