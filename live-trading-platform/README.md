# Live Trading Platform

A self-improving algorithmic paper trading platform that uses **100% live market data** (no mock/synthetic data fallbacks), runs autonomous trading strategies, and provides a real-time web dashboard.

## Features
- 100% live market data (Kraken, Binance, Coinbase, Alpaca)
- Per-asset-class ledgers with strict accounting isolation
- Autonomous trading with Moving Average Crossover and Momentum strategies
- AI strategy research, backtesting, and parameter optimization
- Self-improvement engine with health monitoring and rollback
- Real-time web dashboard with live prices, positions, trades, and charts
- Advanced order types: MARKET, LIMIT, STOP-LOSS, STOP-LIMIT, TRAILING STOP, TAKE-PROFIT
- Technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV, Stochastic, Williams R, ADX, Ichimoku, Fibonacci
- Price alerts and indicator alerts with WebSocket notifications
- Watchlist management
- Trade history CSV export
- Exchange adapter template system for easy addition of new exchanges

## Quick Start
```bash
cd live-trading-platform
python main.py web --port 9000
```

Open http://localhost:9000 in your browser.

## Run Tests
```bash
python3 -m unittest tests.test_platform -v
```

## Architecture
See `live-trading-platform-build-prompt.md` for the complete specification.
