# 布林带回踩EMA20交易策略

## 📋 策略概述

这是一个基于Freqtrade框架开发的量化交易策略，专门针对15分钟时间框架设计。策略的核心思想是捕捉价格突破布林带后回踩EMA20的交易机会。

### 🎯 策略逻辑

**做多信号：**
1. 价格收盘突破布林带上轨
2. 随后价格回踩至EMA20附近
3. 在EMA20附近设置限价买单入场

**做空信号：**
1. 价格收盘跌破布林带下轨  
2. 随后价格反弹至EMA20附近
3. 在EMA20附近设置限价卖单入场

## 📊 技术指标

- **布林带 (Bollinger Bands)**: 周期20，标准差2.0，识别价格突破
- **EMA20**: 作为关键的支撑/阻力位
- **RSI (14)**: 用于动量确认，避免极端超买超卖
- **成交量**: 确认突破的有效性

## ⚡ 风险管理

- **止损**: 3% 固定止损
- **追踪止损**: 启用，盈利2%开始追踪，3%触发
- **止盈**: 多级止盈 (2%-8%)
- **最大持仓**: 3个同时持仓
- **杠杆**: 2倍 (保守设置)

## 🚀 快速开始

### 1. 环境准备

确保已安装Freqtrade：
```bash
# 如果未安装，请先安装Freqtrade
pip install freqtrade
# 或使用Docker版本
```

### 2. 策略测试

运行回测脚本：
```bash
cd /home/user/webapp
python backtest_bollinger_ema.py
```

### 3. 参数优化

运行超参数优化：
```bash
python hyperopt_bollinger_ema.py
```

### 4. 实盘配置

使用提供的配置文件：
```bash
cp user_data/bollinger_ema_config.json config.json
# 编辑config.json，填入您的交易所API信息
```

## 📁 文件结构

```
user_data/
├── strategies/
│   └── BollingerEmaRetraceStrategy.py    # 主策略文件
│   └── OptimizedBollingerEmaStrategy.py  # 优化后策略 (运行hyperopt后生成)
├── bollinger_ema_config.json             # 策略配置文件
backtest_bollinger_ema.py                 # 回测脚本
hyperopt_bollinger_ema.py                 # 参数优化脚本
```

## 🔧 参数说明

### 可优化参数

| 参数名 | 范围 | 默认值 | 说明 |
|--------|------|--------|------|
| `bb_period` | 15-25 | 20 | 布林带周期 |
| `bb_std` | 1.8-2.5 | 2.0 | 布林带标准差 |
| `ema_period` | 15-25 | 20 | EMA周期 |
| `retrace_candles` | 2-8 | 5 | 回踩确认K线数 |
| `bb_break_strength` | 0.001-0.01 | 0.005 | 突破强度阈值 |

### 固定参数

- **时间框架**: 15分钟
- **交易模式**: 支持做多做空
- **订单类型**: 限价单入场，限价单出场
- **止损类型**: 市价止损

## 📈 使用示例

### 基本回测

```bash
# 下载数据并回测
python -m freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 15m --days 30 --trading-mode futures

python -m freqtrade backtesting \
  --strategy BollingerEmaRetraceStrategy \
  --timeframe 15m \
  --pairs BTC/USDT ETH/USDT \
  --timerange 20240101-
```

### 参数优化

```bash
python -m freqtrade hyperopt \
  --strategy BollingerEmaRetraceStrategy \
  --timeframe 15m \
  --epochs 100 \
  --spaces buy \
  --hyperopt-loss SharpeHyperOptLoss
```

### 实盘运行

```bash
python -m freqtrade trade --config config.json --strategy BollingerEmaRetraceStrategy
```

## ⚠️ 重要提醒

1. **测试优先**: 请务必在模拟环境中充分测试后再进行实盘交易
2. **资金管理**: 建议单次投入资金不超过总资金的20%
3. **参数调优**: 不同市场环境可能需要调整参数
4. **监控必要**: 实盘运行时需要定期监控策略表现

## 📊 预期表现

基于历史回测数据 (具体数据需要运行回测后获得)：
- **年化收益率**: 待测试
- **最大回撤**: 待测试  
- **夏普比率**: 待测试
- **胜率**: 待测试

## 🔍 进一步优化建议

1. **多时间框架**: 考虑结合更高时间框架的趋势确认
2. **市场状态**: 添加市场波动率或趋势强度过滤
3. **动态参数**: 根据市场条件动态调整参数
4. **止损优化**: 考虑ATR或波动率自适应止损

## 📞 支持与反馈

如有问题或建议，请：
1. 检查Freqtrade官方文档
2. 分析回测结果和日志文件
3. 调整策略参数并重新测试

---

**风险提示**: 量化交易存在损失风险，请谨慎操作，仅投入可承受损失的资金。