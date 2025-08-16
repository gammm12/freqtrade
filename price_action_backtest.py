#!/usr/bin/env python3
"""
Al Brooks价格行为策略回测和分析脚本
"""

import os
import sys
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
import json

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
            print(result.stdout[:2000])  # 限制输出长度
            if len(result.stdout) > 2000:
                print("... (输出已截断)")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print("❌ 失败!")
        print("错误信息:")
        print(e.stderr)
        return False, e.stderr

def analyze_price_action_signals():
    """分析价格行为信号的理论基础"""
    
    print("\n📊 Al Brooks价格行为理论分析框架")
    
    analysis = """
    
    🎯 Always In 状态机理论基础:
    ==========================================
    
    1. 市场状态分类:
       • Trend Up (始终在多): 强势上涨，持续做多思维
       • Trend Down (始终在空): 强势下跌，持续做空思维  
       • Range (震荡): 无明确方向，区间交易
    
    2. 状态转换条件:
       • 强突破启动: 收盘价突破 + ATR倍数确认 + 强信号棒
       • 趋势维持: 连续强势K线 + 动能延续
       • 状态降级: 重叠增加 + 实体缩小 + 方向不明
    
    🔍 四大核心策略模块:
    ==========================================
    
    策略1: 趋势延续 (Trend Continuation)
    • 识别强趋势中的延续机会
    • 关键: Always In状态 + 强收盘棒 + 高级别确认
    • 目标: 测量移动完成(约70%概率)
    
    策略2: 突破回踩 (Breakout-Pullback)  
    • 捕捉突破后的健康回调入场
    • 关键: 有效突破 + 浅回踩(≤50%) + 反弹确认
    • Brooks: "初学者用止损单，不要抄底抄顶"
    
    策略3: 楔形反转 (Wedge Reversal)
    • 三推结构中的动能衰减识别
    • 关键: 价格新高/新低 + 动能递减 + 反转确认
    • 高概率反转setup，但需严格风控
    
    策略4: 双顶双底 (Double Top/Bottom)
    • 主要vs次要趋势反转区分
    • 关键: 测试失败 + 信号棒质量 + 背景分析
    • 强趋势中谨慎，震荡中积极
    
    📏 测量移动 (Measured Move) 理论:
    ==========================================
    
    Brooks经验法则:
    • "巨大且背景良好的突破有约70%概率走出测量移动"
    • 计算方法: 区间高度 / 突破段长度 / ATR倍数
    • 分批止盈: 1R保本 + 测量移动目标
    
    🎚️ 概率权衡框架:
    ==========================================
    
    交易者方程式: 概率 × 盈亏比 > 1
    • 高概率低回报 vs 低概率高回报
    • Always In简化决策，减少主观判断
    • "保本还是持有"的永恒权衡
    
    🚫 过滤机制:
    ==========================================
    
    1. 震荡市识别: 重叠度 + 实体占比 + 影线特征
    2. 多时间框架: 15m确认 + 5m执行
    3. 成交量确认: 突破需要量能配合
    4. RSI过滤: 避免极端超买超卖
    
    ⚖️ 风险管理哲学:
    ==========================================
    
    • 基于ATR的动态止损(而非固定百分比)
    • 状态驱动的杠杆调整
    • 分批建仓和止盈
    • 连续亏损保护机制
    
    """
    
    print(analysis)

def main():
    """主函数"""
    print("🚀 Al Brooks价格行为策略回测系统")
    print("基于《Reading Price Charts Bar by Bar》理论实现")
    
    # 分析理论基础
    analyze_price_action_signals()
    
    # 1. 检查策略文件
    strategy_path = "/home/user/webapp/user_data/strategies/PriceActionStrategy.py"
    if not os.path.exists(strategy_path):
        print(f"❌ 策略文件不存在: {strategy_path}")
        return False
    
    print(f"\n✅ 策略文件存在: {strategy_path}")
    
    # 2. 验证策略语法
    print("\n🔍 验证价格行为策略语法...")
    command = "python -c \"from user_data.strategies.PriceActionStrategy import PriceActionStrategy; print('Al Brooks价格行为策略语法检查通过'); print(f'支持信号类型: {[e.value for e in PriceActionStrategy.__dict__.get(\"SignalType\", [])]}'); print(f'市场状态: {[e.value for e in PriceActionStrategy.__dict__.get(\"MarketState\", [])]}') \""
    success, output = run_command(command, "价格行为策略语法验证")
    
    if not success:
        print("❌ 策略语法验证失败，请检查代码")
        return False
    
    # 3. 下载多时间框架数据
    print("\n📥 下载价格行为分析所需数据...")
    
    pairs = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]
    timeframes = ["5m", "15m"]  # 价格行为需要多时间框架
    
    for pair in pairs:
        for tf in timeframes:
            command = f"python -m freqtrade download-data --exchange binance --timeframes {tf} --pairs {pair} --days 60 --trading-mode futures"
            success, _ = run_command(command, f"下载 {pair} {tf} 数据 (60天)")
            
            if not success:
                print(f"⚠️  {pair} {tf} 数据下载失败，继续...")
    
    # 4. 运行价格行为策略回测
    print("\n📊 运行Al Brooks价格行为策略回测...")
    
    backtest_command = f"""python -m freqtrade backtesting \\
        --strategy PriceActionStrategy \\
        --timeframe 5m \\
        --timerange 20240101- \\
        --pairs BTC/USDT ETH/USDT BNB/USDT SOL/USDT \\
        --starting-balance 10000 \\
        --trading-mode futures \\
        --enable-protections \\
        --breakdown day \\
        --dry-run-wallet 10000"""
    
    success, output = run_command(backtest_command, "Al Brooks价格行为策略回测")
    
    if success:
        print("\n🎉 价格行为策略回测完成!")
        
        # 5. 显示回测结果
        print("\n📈 Al Brooks策略回测结果分析:")
        result_command = "python -m freqtrade backtesting-show --strategy PriceActionStrategy"
        success, result_output = run_command(result_command, "显示价格行为策略回测结果")
        
        # 6. 性能分析
        if success:
            print("\n🔬 价格行为策略性能深度分析:")
            
            performance_analysis = """
            
            📊 关键绩效指标解读:
            ====================================
            
            1. Always In 状态准确性:
               • 查看趋势识别的成功率
               • 状态转换的及时性
               • 震荡市过滤效果
            
            2. 四大策略模块表现:
               • 趋势延续: 胜率 vs 盈亏比
               • 突破回踩: 回调深度统计
               • 楔形反转: 反转成功率
               • 双顶双底: 主要vs次要反转区分
            
            3. 测量移动达成率:
               • 理论70%概率验证
               • 不同市场环境下的表现差异
               • 分批止盈策略效果
            
            4. Brooks理论验证:
               • "80%交易日前90分钟反转"规律
               • 强趋势延续概率
               • 震荡vs趋势市场识别准确性
            
            💡 优化建议方向:
            ====================================
            
            • 参数敏感性分析
            • 不同品种适应性调整  
            • 时间周期优化
            • 风险调整收益率提升
            
            """
            
            print(performance_analysis)
        
    else:
        print("❌ 回测执行失败")
        
    # 7. 策略特点总结
    print("\n📋 Al Brooks价格行为策略特点总结:")
    print("""
    🎯 核心理念:
    • Always In状态机: 始终保持市场方向判断
    • 裸K分析: 基于价格行为，不依赖指标
    • 概率思维: 权衡胜率与盈亏比
    
    🔧 技术特色:
    • 多时间框架共振(15m+5m)
    • ATR动态风控
    • 四大策略模块互补
    • 基于市场结构的状态机
    
    📊 适用场景:
    • 强趋势市场: 趋势延续策略
    • 震荡整理: 突破回踩策略  
    • 转折关口: 楔形与双重反转
    • 全天候交易: Always In理念
    
    ⚠️ 风险提示:
    • 需要充分的历史数据验证
    • 对执行精度要求较高
    • 建议先模拟交易熟悉
    • 定期调整参数适应市场
    """)
    
    return True

if __name__ == "__main__":
    main()