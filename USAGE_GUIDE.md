# Freqtrade 使用指南

![Freqtrade Logo](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/assets/freqtrade_poweredby.svg)

## 目录
- [快速开始](#快速开始)
- [安装指南](#安装指南)
- [基础配置](#基础配置)
- [策略开发](#策略开发)
- [回测分析](#回测分析)
- [实盘交易](#实盘交易)
- [监控与管理](#监控与管理)
- [高级功能](#高级功能)
- [常见问题](#常见问题)
- [安全提示](#安全提示)

## 快速开始

### ⚡ Docker 快速启动（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade

# 2. 使用 Docker Compose 启动
docker-compose up -d

# 3. 创建配置文件
docker-compose exec freqtrade freqtrade new-config --config user_data/config.json
```

### 🐍 原生 Python 安装

```bash
# 1. 克隆项目
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade

# 2. 运行安装脚本
./setup.sh

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 创建用户目录和配置
freqtrade create-userdir --userdir user_data
freqtrade new-config --config user_data/config.json
```

## 安装指南

### 📋 系统要求

**最低硬件要求：**
- 内存：2GB RAM
- 存储：1GB 磁盘空间
- CPU：2vCPU

**软件要求：**
- Python 3.11 或更高版本
- pip（Python 包管理器）
- git
- TA-Lib（技术分析库）

### 💾 安装方法

#### 方法1: 自动安装脚本

**Linux/macOS:**
```bash
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
./setup.sh
```

**Windows:**
```powershell
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
.\setup.ps1
```

#### 方法2: 手动安装

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -e .

# 或安装特定功能版本
pip install freqtrade[hyperopt,plot]  # 包含超参数优化和绘图功能
```

## 基础配置

### 🔧 创建配置文件

```bash
# 创建用户数据目录
freqtrade create-userdir --userdir user_data

# 创建新配置文件
freqtrade new-config --config user_data/config.json
```

### 📝 基础配置示例

```json
{
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": 100,
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "USD",
    "dry_run": true,
    "dry_run_wallet": 1000,
    
    "exchange": {
        "name": "binance",
        "key": "your_api_key",
        "secret": "your_api_secret",
        "ccxt_config": {},
        "ccxt_async_config": {},
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT",
            "ADA/USDT"
        ],
        "pair_blacklist": []
    },
    
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1,
        "price_last_balance": 0.0,
        "check_depth_of_market": {
            "enabled": false,
            "bids_to_ask_delta": 1
        }
    },
    
    "exit_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    },
    
    "pairlists": [
        {
            "method": "StaticPairList"
        }
    ],
    
    "telegram": {
        "enabled": true,
        "token": "your_telegram_bot_token",
        "chat_id": "your_telegram_chat_id"
    },
    
    "initial_state": "running",
    "force_entry_enable": false,
    "internals": {
        "process_throttle_secs": 5
    }
}
```

### 🔑 API 密钥配置

1. **交易所 API 设置**
   - 在交易所创建 API 密钥
   - 设置必要的权限（只读、交易）
   - **重要：** 不要授予提现权限

2. **Telegram Bot 设置**
   ```bash
   # 1. 联系 @BotFather 创建 Bot
   # 2. 获取 Bot Token
   # 3. 获取 Chat ID（发送消息给 @userinfobot）
   ```

## 策略开发

### 📊 创建自定义策略

```bash
# 创建新策略文件
freqtrade new-strategy --strategy MyCustomStrategy --template minimal
```

### 🎯 策略示例

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class MyCustomStrategy(IStrategy):
    # 策略基本设置
    INTERFACE_VERSION = 3
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
    stoploss = -0.10
    timeframe = '5m'
    
    # 技术指标
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']
        
        return dataframe
    
    # 买入信号
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &  # RSI 超卖
                (dataframe['macd'] > dataframe['macdsignal']) &  # MACD 金叉
                (dataframe['close'] <= dataframe['bb_lowerband'])  # 价格触及下轨
            ),
            'enter_long'] = 1
        
        return dataframe
    
    # 卖出信号
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |  # RSI 超买
                (dataframe['close'] >= dataframe['bb_upperband'])  # 价格触及上轨
            ),
            'exit_long'] = 1
        
        return dataframe
```

### 🔍 策略测试

```bash
# 检查策略语法
freqtrade show-strategies --strategy MyCustomStrategy

# 测试策略运行
freqtrade test-pairlist --config user_data/config.json --strategy MyCustomStrategy
```

## 回测分析

### 📥 下载历史数据

```bash
# 下载特定交易对的数据
freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 5m 1h --days 30

# 下载所有白名单交易对数据
freqtrade download-data --config user_data/config.json --timeframes 5m 1h --days 90
```

### 🔄 运行回测

```bash
# 基础回测
freqtrade backtesting --config user_data/config.json --strategy MyCustomStrategy --timeframe 5m

# 详细回测（包含详细日志）
freqtrade backtesting \
    --config user_data/config.json \
    --strategy MyCustomStrategy \
    --timeframe 5m \
    --timerange=20231001-20231201 \
    --export trades \
    --breakdown day month
```

### 📈 回测结果分析

```bash
# 显示回测结果
freqtrade backtesting-show

# 分析回测结果
freqtrade backtesting-analysis --config user_data/config.json

# 生成回测报告图表
freqtrade plot-dataframe --config user_data/config.json --strategy MyCustomStrategy --timeframe 5m
freqtrade plot-profit --config user_data/config.json
```

## 实盘交易

### ⚠️ 开始前的检查清单

- [ ] 策略经过充分回测
- [ ] 在干跑模式下测试至少1周
- [ ] API 密钥权限正确设置
- [ ] 资金管理参数合理
- [ ] 风险控制措施到位

### 🚀 启动实盘交易

```bash
# 1. 首先在干跑模式测试
freqtrade trade --config user_data/config.json --strategy MyCustomStrategy --dry-run

# 2. 确认无误后，启动实盘交易
freqtrade trade --config user_data/config.json --strategy MyCustomStrategy
```

### 🛡️ 安全配置

```json
{
    "max_open_trades": 3,
    "stake_amount": 50,  // 每笔交易金额
    "tradable_balance_ratio": 0.95,  // 可交易资金比例
    "stoploss": -0.10,  // 全局止损
    "trailing_stop": true,  // 追踪止损
    "trailing_stop_positive": 0.02,
    "trailing_only_offset_is_reached": true,
    "unfilledtimeout": {
        "entry": 10,  // 进场订单超时（分钟）
        "exit": 30    // 出场订单超时（分钟）
    }
}
```

## 监控与管理

### 📱 Telegram 控制

**基本命令：**
```
/start - 启动交易
/stop - 停止交易
/status - 查看当前状态
/profit - 查看盈亏情况
/balance - 查看账户余额
/performance - 查看交易表现
/daily 7 - 查看最近7天日收益
/forceexit <trade_id> - 强制平仓
```

**高级命令：**
```
/reload_config - 重新加载配置
/show_config - 显示当前配置
/stopentry - 停止开新仓
/edge - 查看 Edge 分析
/version - 查看版本信息
```

### 🌐 Web UI 界面

```bash
# 安装 Web UI
freqtrade install-ui

# 启动 Web 服务器
freqtrade webserver --config user_data/config.json
```

Web UI 功能：
- 实时交易监控
- 策略性能分析
- 配置管理
- 交易历史查看
- 图表分析

### 📊 性能监控

```bash
# 查看交易历史
freqtrade show-trades --config user_data/config.json

# 查看详细统计
freqtrade show-trades --config user_data/config.json --print-json

# 导出交易数据
freqtrade show-trades --config user_data/config.json --db-url sqlite:///user_data/tradesv3.sqlite --trade-source DB
```

## 高级功能

### 🤖 FreqAI 机器学习

```json
{
    "freqai": {
        "enabled": true,
        "identifier": "example_freqai_strat",
        "feature_parameters": {
            "include_timeframes": ["5m", "15m", "4h"],
            "include_corr_pairlist": ["ETH/USDT", "LINK/USDT"],
            "label_period_candles": 24,
            "include_shifted_candles": 2,
            "DI_threshold": 0.9,
            "weight_factor": 0.9,
            "principal_component_analysis": false,
            "use_SVM_to_remove_outliers": true,
            "svm_params": {"shuffle": true, "nu": 0.1}
        },
        "data_split_parameters": {
            "test_size": 0.33,
            "shuffle": false
        },
        "model_training_parameters": {
            "n_estimators": 800
        }
    }
}
```

### ⚡ 超参数优化

```bash
# 运行超参数优化
freqtrade hyperopt \
    --config user_data/config.json \
    --hyperopt-loss SharpeHyperOptLoss \
    --strategy MyCustomStrategy \
    --epochs 1000 \
    --spaces buy sell roi stoploss

# 查看优化结果
freqtrade hyperopt-list --best

# 显示最佳参数详情
freqtrade hyperopt-show -n -1
```

### 🔄 策略优化工具

```bash
# 前瞻性偏差检测
freqtrade lookahead-analysis --config user_data/config.json --strategy MyCustomStrategy

# 递归分析
freqtrade recursive-analysis --config user_data/config.json --strategy MyCustomStrategy
```

## 常见问题

### ❓ 常见错误及解决方案

**1. API 连接错误**
```bash
# 检查 API 密钥和权限
freqtrade list-markets --config user_data/config.json
```

**2. 数据下载失败**
```bash
# 检查网络连接和交易所状态
freqtrade list-exchanges
```

**3. 策略错误**
```bash
# 验证策略语法
freqtrade show-strategies --strategy MyCustomStrategy --config user_data/config.json
```

**4. 回测数据不足**
```bash
# 下载更多历史数据
freqtrade download-data --days 365
```

### 🔧 性能优化

**1. 提高回测速度**
```json
{
    "process_throttle_secs": 1,
    "internals": {
        "process_throttle_secs": 1,
        "heartbeat_interval": 60
    }
}
```

**2. 内存使用优化**
```bash
# 使用较小的时间范围进行回测
freqtrade backtesting --timerange=20231101-20231201
```

### 📝 日志配置

```json
{
    "verbosity": 3,
    "logfile": "logs/freqtrade.log",
    "refresh_period": 1800
}
```

## 安全提示

### 🔒 安全最佳实践

1. **API 安全**
   - 使用只读 + 交易权限，避免提现权限
   - 定期更换 API 密钥
   - IP 白名单限制

2. **资金安全**
   - 从小资金开始
   - 设置合理的风险参数
   - 定期监控交易表现

3. **策略安全**
   - 充分回测验证
   - 干跑模式测试
   - 多市场条件验证

4. **系统安全**
   - 定期备份配置和数据
   - 使用防火墙保护
   - 及时更新软件版本

### ⚠️ 重要声明

- 本软件仅供教育目的使用
- 加密货币交易存在高风险
- 不要投入无法承受损失的资金
- 作者不承担任何交易损失责任
- 强烈建议具备编程和交易知识

### 📞 获取帮助

- **官方文档**: https://www.freqtrade.io
- **Discord 社区**: https://discord.gg/p7nuUNVfP7
- **GitHub Issues**: https://github.com/freqtrade/freqtrade/issues
- **Stack Overflow**: 使用 `freqtrade` 标签

---

## 结语

Freqtrade 是一个功能强大的交易机器人，但成功的自动化交易需要：
- 深入理解市场机制
- 扎实的编程基础
- 严格的风险管理
- 持续的学习和优化

祝您交易愉快，收益稳定！ 🚀

---
*最后更新: 2025年8月*