# CryptoAI News - AI Crypto News Aggregator 📰

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue">
  <img src="https://img.shields.io/badge/Python-3.9+-green">
</p>

## 📰 Overview

CryptoAI News delivers AI-powered crypto news directly to Telegram. Get real-time news, smart summaries, sentiment analysis, and coin-specific filtering.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📰 **Real-time News** | Aggregated from top crypto sources |
| 🧠 **AI Summaries** | GPT-4 powered article summaries |
| 📈 **Sentiment Analysis** | Bullish/Bearish indicators |
| 💎 **Coin Filtering** | Filter by specific coins |
| 🔔 **Alerts** | Real-time notifications |
| 💬 **Telegram Bot** | Access anywhere |

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| 🆓 Free | $0 | 5 news/day |
| ⭐ Pro | $12/mo | Unlimited + alerts |
| 💎 VIP | $24/mo | Early access |

## 🚀 Quick Start

```bash
cd crypto-news-ai
pip install -r requirements.txt
cp config.yaml config.yaml
# Add your keys

python bot/telegram_bot.py

# Run tests
python tests/test_core.py
```

## 📁 Structure

```
crypto-news-ai/
├── bot/telegram_bot.py       # Beautiful Telegram bot
├── core/news_generator.py    # AI news engine
├── dashboard/admin.py         # Analytics
├── payments/                # Stripe
├── tests/test_core.py        # Tests
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
📰 CRYPTONEWS AI TEST SUITE
==================================================

🧪 Testing News Aggregator...
   ✅ XX coins tracked: PASS
   ✅ News Aggregator tests PASSED

🧪 Testing Sentiment Analysis...
   ✅ Sentiment: bullish 🐂: PASS
   ✅ Sentiment tests PASSED

🧪 Testing News Fetch...
   ✅ XX articles fetched: PASS
   ✅ News Fetch tests PASSED

🧪 Testing Message Formatting...
   ✅ Formatted message: XXX chars: PASS
   ✅ Message Formatting tests PASSED

🧪 Testing Database...
   ✅ User creation: PASS
   ✅ Database tests PASSED

==================================================
✅ ALL TESTS PASSED!
==================================================
```

## 🎨 Beautiful UI

```
╔══════════════════════════════════════╗
║         📰 CRYPTONEWS 📰            ║
╚══════════════════════════════════════╝

🐂 BULLISH 🐂

📰 Bitcoin Surges Past $100K...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Summary:
Bitcoin has broken through the $100,000...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️ Coins: $BTC $ETH
📡 Source: CoinDesk
⏰ 2h ago

🔗 Read More
```

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/news` | Latest news |
| `/search bitcoin` | News for coin |
| `/coins` | Tracked coins |
| `/sentiment` | Market mood |
| `/upgrade` | Premium plans |

## 📊 Supported Coins

Bitcoin, Ethereum, Solana, Cardano, Polkadot, Ripple, Chainlink, Polygon, Uniswap, Avalanche

## 🔐 Config

```yaml
openai_api_key: "your-key"
telegram_bot_token: "your-token"
stripe_api_key: "sk_test_..."
newsapi_key: "your-key"
```

## ⚠️ Disclaimer

News is for informational purposes only. Not financial advice.

## 🤝 Similar

- CoinDesk ($500M)
- CryptoPanic ($10M+)

## ✅ Differentiation

- AI summarization (unique)
- Telegram-first
- Sentiment analysis
- Cheaper
