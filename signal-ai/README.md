# SignalAI - AI Crypto Trading Signals 📈

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue">
  <img src="https://img.shields.io/badge/Python-3.9+-green">
</p>

## 📈 Overview

SignalAI delivers AI-powered crypto trading signals directly through Telegram. Get entry/exit points, stop-loss recommendations, and market analysis with beautiful UI.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Trading Signals** | Entry, target, and stop-loss prices |
| 🧠 **AI Analysis** | GPT-4 powered market analysis |
| 💎 **Beautiful UI** | Rich formatted Telegram messages |
| 📊 **10+ Coins** | Bitcoin, Ethereum, Solana, and more |
| 👀 **Watchlist** | Track your favorite coins |
| 🔔 **Alerts** | Real-time signal notifications |

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| 🆓 Free | $0 | 3 signals/week |
| ⭐ Pro | $19/mo | Unlimited + daily analysis |
| 💎 VIP | $49/mo | Early signals + private group |

## 🚀 Quick Start

```bash
cd signal-ai
pip install -r requirements.txt
cp config.yaml config.yaml
# Add your keys

python bot/telegram_bot.py

# Run tests
python tests/test_core.py
```

## 📁 Structure

```
signal-ai/
├── bot/telegram_bot.py      # Beautiful Telegram bot
├── core/signal_generator.py # AI signal engine
├── dashboard/admin.py        # Analytics
├── payments/               # Stripe
├── tests/test_core.py       # Tests
├── config.yaml
└── README.md
```

## 🧪 Testing

```bash
python tests/test_core.py
```

Output:
```
==================================================
📈 SIGNALAI TEST SUITE
==================================================

🧪 Testing Signal Generator...
   ✅ XX coins loaded: PASS
   ✅ Signal Generator tests PASSED

🧪 Testing Signal Creation...
   ✅ Signal: 🟢 BUY BTC
   ✅ Entry: $XX,XXX.XX
   ✅ Target: $XX,XXX.XX
   ✅ Signal Creation tests PASSED

🧪 Testing Message Formatting...
   ✅ Formatted message: XXX chars
   ✅ Message Formatting tests PASSED

🧪 Testing Database...
   ✅ User creation: PASS
   ✅ Database tests PASSED

==================================================
✅ ALL TESTS PASSED!
==================================================
```

## 🎨 Beautiful UI

SignalAI features rich Telegram messages:

```
╔══════════════════════════════════════╗
║       🚀 AI TRADING SIGNAL 🚀        ║
╚══════════════════════════════════════╝

🟢 🟢 BUY 🟢 

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 Bitcoin (BTC)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Entry Price: $45,000.00
🎯 Target: $52,000.00 (+15.5%)
🛡️ Stop Loss: $42,000.00 (-6.6%)

⏱️ Timeframe: 4h
🔥 Confidence: 85%

📝 Analysis:
Strong momentum detected...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/signal` | Get trading signal |
| `/coins` | View tracked coins |
| `/signals` | Recent signals |
| `/watchlist` | Your watchlist |
| `/upgrade` | Premium plans |
| `/help` | Help menu |

## 📊 Supported Coins

- Bitcoin (BTC)
- Ethereum (ETH)
- Solana (SOL)
- Cardano (ADA)
- Polkadot (DOT)
- Avalanche (AVAX)
- Chainlink (LINK)
- Polygon (MATIC)
- Uniswap (UNI)
- XRP (XRP)

## 🔐 Configuration

```yaml
openai_api_key: "your-openai-key"
telegram_bot_token: "your-telegram-token"
stripe_api_key: "sk_test_..."
```

## ⚠️ Disclaimer

Trading cryptocurrencies involves substantial risk. Signals are for educational purposes only. Always do your own research before trading.

## 🤝 Similar Products

- TradingView ($100M+)
- CoinSignals
- BitcoinWisdom

## ✅ Differentiation

- AI-powered analysis
- Beautiful Telegram UI
- Cheaper than alternatives
- No app needed
