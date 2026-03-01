# MeetAI - AI Meeting Assistant 🤖

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

## 📹 Overview

MeetAI is an AI-powered meeting assistant that transcribes, summarizes, and extracts action items from your Zoom, Google Meet, and Microsoft Teams meetings. Simply upload audio/video or paste a transcript, and MeetAI generates comprehensive summaries with actionable insights.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Transcription** | AI-powered transcription using OpenAI Whisper |
| 📝 **Smart Summaries** | Multiple summary templates (Standard, Action, Brief, Decision) |
| ✅ **Action Items** | Automatically extract tasks and assignments |
| 🔍 **Searchable Library** | Find past meetings instantly |
| 📤 **Export** | Export to Notion, Todoist, and more |
| 💬 **Telegram Bot** | Access via Telegram - no app install needed |

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| 🆓 **Free** | $0 | 3 meetings/month |
| ⭐ **Pro** | $14/mo | Unlimited meetings, long meetings, priority support |
| 🏢 **Business** | $39/mo | Team features, API access, white-label |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Telegram Bot Token
- OpenAI API Key (optional for testing)

### Installation

```bash
# Clone or navigate to project
cd meet-ai

# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp config.yaml config.yaml
# Edit config.yaml with your API keys
```

### Configuration

Edit `config.yaml`:

```yaml
openai_api_key: "your-openai-api-key"
telegram_bot_token: "your-telegram-bot-token"
stripe_api_key: "sk_test_..."
```

### Running

```bash
# Start the bot
python bot/telegram_bot.py

# Run tests
python tests/test_core.py

# View dashboard
python dashboard/admin.py
```

## 📁 Project Structure

```
meet-ai/
├── bot/
│   └── telegram_bot.py      # Telegram bot handlers
├── core/
│   └── meeting_processor.py # AI processing logic
├── dashboard/
│   └── admin.py            # Admin analytics
├── payments/
│   └── stripe_processor.py # Payment processing
├── tests/
│   └── test_core.py        # Test suite
├── config.yaml              # Configuration
├── requirements.txt         # Dependencies
└── README.md              # This file
```

## 🔧 Usage

### Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/new` | Start new meeting |
| `/templates` | View summary templates |
| `/my` | View your meetings |
| `/upgrade` | View subscription plans |
| `/help` | Get help |

### Supported Platforms

- Zoom
- Google Meet
- Microsoft Teams
- Any recorded meeting (MP3, WAV, MP4)

### Summary Templates

1. **standard** - Comprehensive summary with key points
2. **action** - Focus on action items and next steps
3. **brief** - Quick 3-paragraph summary
4. **decision** - Decision log format

## 🧪 Testing

Run the test suite:

```bash
python tests/test_core.py
```

Expected output:
```
==================================================
🧪 MEETAI TEST SUITE
==================================================

🧪 Testing Database...
   ✅ User creation: PASS
   ✅ Get meetings: PASS
   ✅ Database tests PASSED

🧪 Testing Meeting Processor...
   ✅ Get templates: PASS
   ✅ Process meeting: PASS
   📝 Summary: [summary text]
   ✅ Action items: X items
   ✅ Meeting Processor tests PASSED

🧪 Testing Integration...
   ✅ Full integration: PASS
   ✅ Integration tests PASSED

==================================================
✅ ALL TESTS PASSED!
==================================================
```

## 💳 Payments

MeetAI uses Stripe for payments. To set up:

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get your API keys from Stripe Dashboard
3. Add keys to `config.yaml`
4. Configure webhook URL in Stripe

### Price IDs (set in Stripe Dashboard)

- Pro Monthly: $14/mo
- Business Monthly: $39/mo

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 and Whisper |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `STRIPE_API_KEY` | No | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook secret |

## 🤝 Similar Products

MeetAI competes with:
- **Fireflies.ai** - $200M+ valuation
- **Otter.ai** - $100M+ valuation
- **Descript** - Meeting transcription

### Our Differentiation
- ✅ Cheaper pricing
- ✅ Telegram-first (no app needed)
- ✅ Better for small teams

## 📈 Roadmap

- [ ] Browser extension for auto-join
- [ ] Real-time transcription during calls
- [ ] Notion integration
- [ ] Slack integration
- [ ] Team management dashboard

## 🐛 Troubleshooting

### Bot not responding?

1. Check `TELEGRAM_BOT_TOKEN` is set correctly
2. Verify bot is started: `python bot/telegram_bot.py`
3. Check Telegram @BotFather for bot status

### No summary generated?

1. Ensure `OPENAI_API_KEY` is set
2. Check API credits at [platform.openai.com](https://platform.openai.com)
3. Try with shorter transcript for testing

### Payments not working?

1. Verify Stripe keys in `config.yaml`
2. Check Stripe dashboard for errors
3. Ensure webhook is configured

## 📄 License

MIT License - See LICENSE file for details.

## 👤 Author

Built by [Your Name]

## 🙏 Support

- Email: support@meetai.com
- Telegram: @meetai_support

---

<p align="center">Made with ❤️ for productive meetings</p>
