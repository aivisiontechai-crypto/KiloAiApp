# MailAI - AI Email Assistant 📧

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue">
  <img src="https://img.shields.io/badge/Python-3.9+-green">
</p>

## 📧 Overview

MailAI is an AI-powered email writing assistant that helps professionals compose emails faster. Generate replies, cold outreach, follow-ups, and more via Telegram bot.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **6 Email Types** | Reply, Cold Outreach, Follow-up, Meeting Request, Thank You, Introduction |
| 🎨 **5 Tones** | Professional, Casual, Friendly, Formal, Bold |
| 🌐 **5 Languages** | English, Spanish, French, German, Italian |
| 💬 **Telegram Bot** | Access anywhere |

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| 🆓 Free | $0 | 5 emails/week |
| ⭐ Pro | $9/mo | Unlimited + custom tones |
| 🏢 Business | $29/mo | Team features |

## 🚀 Quick Start

```bash
cd mail-ai
pip install -r requirements.txt
cp config.yaml config.yaml
# Add your keys
python bot/telegram_bot.py

# Run tests
python tests/test_core.py
```

## 📁 Structure

```
mail-ai/
├── bot/telegram_bot.py      # Telegram bot
├── core/email_generator.py  # AI email generation
├── dashboard/admin.py        # Analytics
├── payments/                # Stripe
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
🧪 MAILAI TEST SUITE
==================================================

🧪 Testing Email Types...
   ✅ 6 email types: PASS
   ✅ Email Types tests PASSED

🧪 Testing Tones...
   ✅ 5 tones available: PASS
   ✅ Tones tests PASSED

🧪 Testing Email Generation...
   ✅ Generated XXX chars: PASS
   ✅ Email Generation tests PASSED

🧪 Testing Database...
   ✅ User creation: PASS
   ✅ Database tests PASSED

==================================================
✅ ALL TESTS PASSED!
==================================================
```

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot |
| `/write` | Create email |
| `/types` | View email types |
| `/tones` | View tones |
| `/my` | Your emails |
| `/upgrade` | Subscribe |

## 📧 Email Types

1. **reply** - Reply to emails
2. **cold_outreach** - Cold outreach
3. **follow_up** - Follow-up emails
4. **meeting_request** - Meeting requests
5. **thank_you** - Thank you notes
6. **introduction** - Introductions

## 🎨 Tones

- professional
- casual
- friendly
- formal
- bold

## 🔐 Config

```yaml
openai_api_key: "your-key"
telegram_bot_token: "your-token"
stripe_api_key: "sk_test_..."
```

## 🤝 Similar

- Superhuman ($100M ARR)
- Lavender ($50M+)

## ✅ Differentiation

- Telegram-first
- Cheaper
- Better for SMBs
