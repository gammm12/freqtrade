# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development setup
```bash
pip install -e ".[dev]"
pre-commit install
```

### Running tests
```bash
pytest                                          # all tests
pytest tests/test_freqtradebot.py               # single file
pytest tests/test_freqtradebot.py::test_create_trades  # single test
pytest --longrun tests/exchange_online/         # live exchange compat tests (requires API keys)
```

### Linting and type checking
```bash
ruff check .          # linting
ruff format .         # formatting (line length 100)
mypy freqtrade        # type checking
pre-commit run -a     # run all pre-commit hooks (includes ruff, mypy, isort, codespell)
```

### Running the bot
```bash
freqtrade trade --strategy MyStrategy           # live/dry-run trading
freqtrade backtesting --strategy MyStrategy     # backtesting
freqtrade hyperopt --strategy MyStrategy        # hyperparameter optimization
freqtrade download-data --pairs BTC/USDT        # data download
```

## Architecture

### Bot runtime loop

`main.py` → `Worker` → `FreqtradeBot.process()` — the `Worker` class throttles execution per candle/timeframe, manages state transitions (`STOPPED`, `RUNNING`, `PAUSED`, `RELOAD_CONFIG`), and wraps `FreqtradeBot`. `FreqtradeBot` orchestrates every trading iteration: it polls pair signals via the `IStrategy`, manages open trades, places/cancels orders via `Exchange`, and emits notifications via `RPCManager`.

### Strategy system (`freqtrade/strategy/`)

User strategies subclass `IStrategy` (which also inherits `HyperStrategyMixin` for hyperopt). The key lifecycle methods that strategies must implement are `populate_indicators`, `populate_entry_trend`, and `populate_exit_trend`. Strategies are loaded dynamically from `user_data/strategies/` via `StrategyResolver`. The `@informative` decorator (in `informative_decorator.py`) supports multi-timeframe data. Hyperoptable parameters are declared with `IntParameter`, `DecimalParameter`, etc. (defined in `strategy/parameters.py`).

### Exchange layer (`freqtrade/exchange/`)

`Exchange` is a CCXT wrapper with retry logic via the `@retrier` / `@retrier_async` decorators in `exchange/common.py`. Exchange-specific subclasses (Binance, Kraken, Bybit, OKX, etc.) override only exchange-specific behaviour. The `FtHas` TypedDict (`exchange_types.py`) describes per-exchange capabilities. To add a new exchange, subclass `Exchange`, override `_ft_has`, and register the class name in `MAP_EXCHANGE_CHILDCLASS` in `exchange/common.py`.

### DataProvider (`freqtrade/data/dataprovider.py`)

The single interface through which strategies access both historical and live candle data, orderbooks, and producer data (External Message Consumer). During backtesting it slices data per candle to prevent lookahead bias. `DataProvider.get_analyzed_dataframe()` is used for live trading; strategies should not call `Exchange` directly.

### Persistence (`freqtrade/persistence/`)

SQLAlchemy ORM models: `Trade` and `Order` (live/DB-backed), and `LocalTrade` (in-memory, used during backtesting to avoid DB overhead). `PairLocks` enforces cooldown periods. `CustomDataWrapper` provides key-value storage attached to trades. `init_db()` initialises the database and runs migrations.

### RPC / API (`freqtrade/rpc/`)

`RPCManager` holds a list of `RPCHandler` instances (Telegram, Discord, Webhook, `ApiServer`). The `ApiServer` is a FastAPI singleton running in a thread via Uvicorn. REST endpoints are split across `api_v1.py`, `api_backtest.py`, `api_download_data.py`, etc. WebSocket push is handled in `rpc/api_server/ws/`. The `ft_client/` directory is a separate installable package providing a minimal REST client.

### Optimization (`freqtrade/optimize/`)

`Backtesting` replays candle data, running `IStrategy` methods per-candle, storing results as `LocalTrade` objects. `Hyperopt` wraps backtesting with Optuna for parameter search; loss functions live in `optimize/hyperopt_loss/`. Backtest results are cached in `user_data/backtest_results/` as JSON.

### FreqAI (`freqtrade/freqai/`)

Optional ML sub-framework. `IFreqaiModel` is the base class; concrete models inherit from `BaseRegressionModel`, `BaseClassifierModel`, or PyTorch variants in `base_models/`. `FreqaiDataKitchen` handles feature engineering, train/test splits, and normalisation. `FreqaiDataDrawer` manages model persistence and prediction caching per pair.

### Plugins (`freqtrade/plugins/`)

- **PairlistManager**: chains `IPairList` handlers (filters/generators in `plugins/pairlist/`) to produce the active trading pair whitelist. New pairlist handlers must also be registered in `AVAILABLE_PAIRLISTS` in `constants.py`.
- **ProtectionManager**: chains `IProtection` handlers that can lock pairs or all trading after bad trades.

### Configuration (`freqtrade/configuration/`)

`Configuration.get_config()` loads and merges JSON config files. `validate_config_consistency()` performs cross-field validation. The canonical JSON Schema lives in `build_helpers/schema.json` (auto-generated by `build_helpers/extract_config_json_schema.py`, which is also a pre-commit hook). The `Config` TypeAlias is `dict[str, Any]` defined in `constants.py`.

### Resolvers (`freqtrade/resolvers/`)

`IResolver` dynamically imports and instantiates user-defined classes (strategies, FreqAI models, pairlist handlers, hyperopt loss functions) by scanning configured paths using `importlib`. `StrategyResolver`, `ExchangeResolver`, `FreqaiModelResolver`, etc. all extend this base.

## Key conventions

### Exception hierarchy
All exceptions inherit from `FreqtradeException`. Use the most specific subclass:
- `OperationalException` / `ConfigurationError` — fatal, requires restart
- `TemporaryError` / `DDosProtection` — transient, handled by `@retrier`
- `StrategyError` — error in user strategy code
- `DependencyException` / `PricingError` / `ExchangeError` — runtime trade failures

### Testing patterns
- `conftest.py` provides fixtures for `FreqtradeBot`, `Exchange`, mock trades, and config dicts. Import `log_has()` / `log_has_re()` from `tests.conftest` to assert log output.
- `EXMS = "freqtrade.exchange.exchange.Exchange"` is the canonical mock target for exchange methods.
- `CURRENT_TEST_STRATEGY = "StrategyTestV3"` is the default strategy used in unit tests.
- Use `time_machine` for time-dependent tests; use `MagicMock`/`PropertyMock` for exchange responses.
- Backtesting tests use `FtNoDBContext` / `disable_database_use()` to avoid DB setup.

### Style
- Line length 100, enforced by ruff.
- Docstrings use double quotes and reST format (`:param x:`, `:return:`, `:raises KeyError:`).
- All public methods should have docstrings.
- PRs must target the `develop` branch (not `stable`).
- New pairlists/protections/exchanges require entries in `constants.py` registration lists.
