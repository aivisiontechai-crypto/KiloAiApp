# LegalAI - AI Legal Document Assistant ⚖️

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

## 📋 Overview

LegalAI is an AI-powered legal document generator that creates professional legal documents through a Telegram bot. Generate NDAs, contracts, privacy policies, and more in seconds using GPT-4.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **8 Document Types** | NDA, Service Contract, Privacy Policy, Terms of Service, Employment Contract, Demand Letter, Invoice, LLC Agreement |
| 🤖 **AI-Powered** | Uses GPT-4 for accurate, professional legal documents |
| 💰 **Flexible Pricing** | Per-document or subscription plans |
| 📱 **Telegram Bot** | Access anywhere via Telegram |
| 💳 **Stripe Payments** | Secure payment processing |

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| 🆓 **Free** | $0 | 1 document/month |
| ⭐ **Pro** | $29/mo | Unlimited documents, all types |
| 🏢 **Business** | $99/mo | Custom templates, API access |

### Per-Document Pricing

| Document | Price |
|----------|-------|
| NDA | $29 |
| Service Contract | $39 |
| Privacy Policy | $49 |
| Terms of Service | $49 |
| Employment Contract | $59 |
| Demand Letter | $34 |
| Invoice | $19 |
| LLC Agreement | $79 |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Telegram Bot Token
- OpenAI API Key (for AI generation)

### Installation

```bash
# Navigate to project
cd legal-ai

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
legal-ai/
├── bot/
│   └── telegram_bot.py      # Telegram bot handlers
├── core/
│   └── document_generator.py # AI document generation
├── dashboard/
│   └── admin.py            # Admin analytics
├── payments/
│   └── stripe_processor.py # Payment processing
├── tests/
│   └── test_core.py       # Test suite
├── config.yaml              # Configuration
├── requirements.txt         # Dependencies
└── README.md              # This file
```

## 🔧 Usage

### Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/documents` | List available document types |
| `/upgrade` | View subscription plans |
| `/help` | Get help |

### Supported Documents

1. **NDA** - Non-Disclosure Agreement
2. **Service Contract** - Freelance/Service Agreement
3. **Privacy Policy** - Website/App privacy policy
4. **Terms of Service** - User agreement
5. **Employment Contract** - Employment agreement
6. **Demand Letter** - Formal demand letter
7. **Invoice** - Professional invoice
8. **LLC Agreement** - Operating agreement

## 🧪 Testing

Run the test suite:

```bash
python tests/test_core.py
```

Expected output:
```
==================================================
🧪 LEGALAI TEST SUITE
==================================================

🧪 Testing Database...
   ✅ User creation: PASS
   ✅ Database tests PASSED

🧪 Testing Document Generator...
   ✅ Available docs: 8 types
   ✅ NDA template: PASS
   ✅ Document generation: PASS
   📄 Generated X characters
   ✅ Document Generator tests PASSED

🧪 Testing Pricing...
   ✅ All 8 documents have prices
   ✅ Pricing tests PASSED

==================================================
✅ ALL TESTS PASSED!
==================================================
```

## 💳 Payments

LegalAI uses Stripe for payments:

1. Create Stripe account at [stripe.com](https://stripe.com)
2. Get API keys from Stripe Dashboard
3. Add to `config.yaml`
4. Configure webhook for subscription events

### Price IDs (create in Stripe)

- Pro Monthly: $29/mo
- Business Monthly: $99/mo

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `STRIPE_API_KEY` | No | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook secret |

## 🤝 Similar Products

- **LegalZoom** - $700M+ valuation
- **Rocket Lawyer** - $500M+ valuation
- **DocuSign** - $15B+ market cap

### Our Differentiation
- ✅ AI-powered (GPT-4)
- ✅ Telegram-first (no website needed)
- ✅ Much cheaper than traditional legal docs

## 📈 Roadmap

- [ ] More document types
- [ ] Custom template builder
- [ ] Multi-language support
- [ ] E-signature integration
- [ ] Lawyer consultation add-on

## 🐛 Troubleshooting

### Bot not responding?

1. Check `TELEGRAM_BOT_TOKEN` is correct
2. Run `python bot/telegram_bot.py`
3. Check @BotFather for bot status

### Documents not generating?

1. Ensure `OPENAI_API_KEY` is set
2. Check API credits at [platform.openai.com](https://platform.openai.com)
3. Try with simpler variables

### Payments failing?

1. Verify Stripe keys in `config.yaml`
2. Check Stripe dashboard
3. Ensure webhook URL is reachable

## 📄 License

MIT License

## 👤 Author

Built by [Your Name]

## 🙏 Support

- Email: support@legalai.com
- Telegram: @legalai_support

---

<p align="center">⚖️ AI-Powered Legal Documents for Everyone</p>
