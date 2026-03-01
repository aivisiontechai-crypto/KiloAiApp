# PodAI - AI Podcast Generator 🎙️

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

## 🎧 Overview

PodAI transforms any content into a podcast! Convert articles, YouTube videos, and PDFs into natural-sounding audio using AI. Access via Telegram bot - no app install required.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📰 **URL to Podcast** | Convert any article to audio |
| 🎬 **YouTube to Audio** | Extract audio from YouTube videos |
| 📄 **PDF to Podcast** | Turn documents into podcasts |
| 🗣️ **6 AI Voices** | Alloy, Echo, Fable, Onyx, Nova, Shimmer |
| 🌐 **9 Languages** | English, Spanish, French, German, etc. |
| 📝 **Smart Summaries** | AI-generated key points |
| 💬 **Telegram Bot** | Access anywhere |

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| 🆓 **Free** | $0 | 3 podcasts/week |
| ⭐ **Pro** | $12/mo | Unlimited + custom voices |
| 🏢 **Business** | $49/mo | Bulk + API + priority |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Telegram Bot Token
- OpenAI API Key (for TTS)

### Installation

```bash
cd pod-ai

pip install -r requirements.txt

cp config.yaml config.yaml
# Edit config.yaml with your API keys
```

### Configuration

```yaml
openai_api_key: "your-openai-key"
telegram_bot_token: "your-telegram-token"
```

### Running

```bash
# Start bot
python bot/telegram_bot.py

# Run tests
python tests/test_core.py

# View dashboard
python dashboard/admin.py
```

## 📁 Project Structure

```
pod-ai/
├── bot/
│   └── telegram_bot.py      # Telegram bot
├── core/
│   └── podcast_generator.py # AI audio generation
├── dashboard/
│   └── admin.py            # Analytics
├── payments/
│   └── stripe_processor.py # Payments
├── tests/
│   └── test_core.py       # Tests
├── config.yaml
├── requirements.txt
└── README.md
```

## 🔧 Usage

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot |
| `/convert` | Create podcast |
| `/voices` | List voice options |
| `/languages` | List languages |
| `/my` | Your podcasts |
| `/upgrade` | Subscribe |

### Supported Sources

- Articles (any URL)
- YouTube videos
- PDF documents

### Voices

| Voice | Style |
|-------|-------|
| Alloy | Neutral |
| Echo | Male |
| Fable | Male |
| Onyx | Deep Male |
| Nova | Female |
| Shimmer | Soft Female |

### Languages

English, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese

## 🧪 Testing

```bash
python tests/test_core.py
```

Output:
```
==================================================
🧪 PODAI TEST SUITE
==================================================

🧪 Testing Database...
   ✅ User creation: PASS
   ✅ Database tests PASSED

🧪 Testing Podcast Generator...
   ✅ Available voices: 6
   ✅ Available languages: 9
   ✅ Templates: PASS
   ✅ Podcast generation: PASS
   📝 Title: [title]...
   ⏱ Duration: ~XXX seconds
   ✅ Podcast Generator tests PASSED

🧪 Testing Pricing...
   ✅ All 6 expected voices available
   ✅ Pricing tests PASSED

==================================================
✅ ALL TESTS PASSED!
==================================================
```

## 💳 Payments

Stripe integration for subscriptions:

1. Create Stripe account
2. Get API keys
3. Add to `config.yaml`
4. Set up webhook

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI for TTS |
| `ELEVENLABS_API_KEY` | No | ElevenLabs (better voices) |
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token |

## 🤝 Similar Products

- **Audify** - Audio content platform
- **Listnr** - Text-to-speech
- **PodcastAI** - AI podcasting

### Our Differentiation
- ✅ Telegram-first (no app)
- ✅ YouTube conversion
- ✅ Cheaper pricing

## 📈 Roadmap

- [ ] Video generation
- [ ] Multiple speakers
- [ ] Background music
- [ ] Podcast hosting
- [ ] RSS feed generation

## 🐛 Troubleshooting

### No audio?

- Check `OPENAI_API_KEY`
- Verify credits at platform.openai.com

### Bot not working?

- Check Telegram token
- Verify bot is running

## 📄 License

MIT

---

<p align="center">🎙️ Turn Any Content Into Podcasts</p>
