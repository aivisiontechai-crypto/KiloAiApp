#!/usr/bin/env python3
"""
PodAI - Telegram Bot
AI Podcast Generator
"""

import os
import asyncio
import uuid
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.podcast_generator import PodcastGenerator, PodcastDatabase, VOICES, LANGUAGES

CONFIG = {"telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "")}


class PodAIBot:
    def __init__(self):
        self.generator = PodcastGenerator()
        self.db = PodcastDatabase()
        self.user_sessions = {}
    
    async def start(self, update, context):
        user = update.effective_user
        self.db.add_user(user.id, user.username or "unknown", "telegram")
        
        welcome = """🎙️ Welcome to PodAI

Turn any content into a podcast!

I can convert:
• Articles (URL)
• YouTube videos
• PDFs

Features:
• Natural AI voices
• Multiple languages
• Quick summaries
• Custom voices

Get started:
/convert - Create podcast
/voices - See voice options
/my podcasts - Your library
/upgrade - Subscribe
/help - More info"""
        await context.bot.send_message(chat_id=user.id, text=welcome)
    
    async def help_command(self, update, context):
        help_text = """🎙️ PodAI Help

/convert - Start creating a podcast
/voices - Available AI voices
/languages - Available languages
/my - Your podcast library
/upgrade - Pro plans
/usage - See your usage

Prices:
Free: 3 podcasts/week
Pro: $12/mo unlimited
Business: $49/mo + API"""
        await update.message.reply_text(help_text)
    
    async def voices_command(self, update, context):
        voices = self.generator.get_voices()
        text = "🎙️ Available Voices\n\n"
        
        for voice_id, info in voices.items():
            text += f"• {voice_id}: {info['name']} ({info['gender']})\n"
        
        text += "\nUse /convert to create your podcast!"
        await update.message.reply_text(text)
    
    async def languages_command(self, update, context):
        langs = self.generator.get_languages()
        text = "🌐 Available Languages\n\n"
        
        for code, name in langs.items():
            text += f"• {code}: {name}\n"
        
        await update.message.reply_text(text)
    
    async def convert_command(self, update, context):
        """Start podcast creation"""
        user = update.effective_user
        
        # Check subscription
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        podcasts_used = user_data.get("podcasts_used", 0) if user_data else 0
        
        if tier == "free" and podcasts_used >= 3:
            await update.message.reply_text("❌ Weekly limit reached (3 podcasts)\n\nUpgrade to Pro for unlimited!\n/upgrade")
            return
        
        # Show voice options
        voices = self.generator.get_voices()
        text = "🎙️ Create a Podcast\n\n"
        text += "Send me a URL to convert!\n"
        text += "Supports:\n"
        text += "• Articles (paste URL)\n"
        text += "• YouTube videos (paste URL)\n"
        text += "• PDFs (send file)\n\n"
        text += "Default voice: alloy (neutral)\n"
        text += "Change with: /voice [name]\n"
        text += "See all: /voices"
        
        self.user_sessions[user.id] = {"step": "waiting_for_url"}
        await update.message.reply_text(text)
    
    async def handle_message(self, update, context):
        text = update.message.text
        user = update.effective_user
        
        if text.startswith("/"):
            return  # Command handled elsewhere
        
        # Check if waiting for URL
        session = self.user_sessions.get(user.id, {})
        
        if session.get("step") == "waiting_for_url" or "youtube" in text.lower() or "http" in text.lower():
            await self.create_podcast(update, context, text)
        else:
            await update.message.reply_text("Use /convert to create a podcast!")
    
    async def create_podcast(self, update, context, url: str):
        user = update.effective_user
        
        # Determine source type
        if "youtube.com" in url or "youtu.be" in url:
            source_type = "youtube"
        elif url.endswith(".pdf"):
            source_type = "pdf"
        else:
            source_type = "url"
        
        # Get user preferences
        user_data = self.db.get_user(user.id)
        voice = user_data.get("voice", "alloy") if user_data else "alloy"
        language = user_data.get("language", "en") if user_data else "en"
        
        # Generate podcast
        await update.message.reply_text("🎙️ Generating your podcast...\nThis takes ~30 seconds.")
        
        try:
            result = await self.generator.generate_podcast(
                source_type=source_type,
                source_url=url,
                voice=voice,
                language=language
            )
            
            # Save
            result["source_url"] = url
            self.db.save_podcast(result, user.id)
            
            # Send to user
            await context.bot.send_message(
                chat_id=user.id,
                text=f"🎙️ *Your Podcast is Ready!*\n\n"
                     f"*{result['title']}*\n\n"
                     f"⏱ Duration: ~{result['duration_seconds']} seconds\n"
                     f"🗣️ Voice: {result['voice']}\n"
                     f"📝 Summary:\n{result['summary'][:300]}...",
                parse_mode="Markdown"
            )
            
            # Send audio (placeholder)
            if result.get("audio_url"):
                await context.bot.send_message(chat_id=user.id, text=f"🔗 Audio: {result['audio_url']}")
            else:
                await context.bot.send_message(chat_id=user.id, text="⚠️ Audio generation pending. Check /my for updates.")
        
        except Exception as e:
            await context.bot.send_message(chat_id=user.id, text=f"❌ Error: {str(e)}")
    
    async def my_podcasts(self, update, context):
        """Show user's podcasts"""
        user = update.effective_user
        podcasts = self.db.get_user_podcasts(user.id, limit=10)
        
        if not podcasts:
            await update.message.reply_text("No podcasts yet! Use /convert to create one.")
            return
        
        text = "🎙️ Your Podcasts\n\n"
        for i, pod in enumerate(podcasts, 1):
            text += f"{i}. {pod['title'][:40]}...\n"
            text += f"   ⏱ {pod['duration']}s | {pod['source_type']} | {pod['created'][:10]}\n"
        
        await update.message.reply_text(text)
    
    async def upgrade_command(self, update, context):
        """Show upgrade options"""
        text = """💳 Upgrade to Pro

🆓 Free: 3 podcasts/week
⭐ Pro ($12/mo): Unlimited + custom voices + priority
🏢 Business ($49/mo): Bulk + API + white-label

Reply with "pro" or "business" to upgrade!"""
        await update.message.reply_text(text)


def run_bot():
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    
    if not CONFIG["telegram_token"]:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = PodAIBot()
    app = Application.builder().token(CONFIG["telegram_token"]).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("convert", bot.convert_command))
    app.add_handler(CommandHandler("voices", bot.voices_command))
    app.add_handler(CommandHandler("languages", bot.languages_command))
    app.add_handler(CommandHandler("my", bot.my_podcasts))
    app.add_handler(CommandHandler("upgrade", bot.upgrade_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("🎙️ PodAI Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
