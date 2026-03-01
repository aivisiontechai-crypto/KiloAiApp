#!/usr/bin/env python3
"""
MeetAI - Telegram Bot
AI Meeting Summarizer
"""

import os
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.meeting_processor import MeetingProcessor, MeetingDatabase

CONFIG = {"telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "")}


class MeetAIBot:
    def __init__(self):
        self.processor = MeetingProcessor()
        self.db = MeetingDatabase()
        self.user_sessions = {}
    
    async def start(self, update, context):
        user = update.effective_user
        self.db.add_user(user.id, user.username or "unknown", "telegram")
        
        welcome = """📹 Welcome to MeetAI

Your AI meeting assistant!

I can:
• Transcribe meetings
• Generate summaries
• Extract action items
• Create decision logs

Get started:
/new - Start new meeting
/templates - Summary styles
/my - Your meetings
/upgrade - Subscribe
/help - More info"""
        await context.bot.send_message(chat_id=user.id, text=welcome)
    
    async def help_command(self, update, context):
        help_text = """📹 MeetAI Help

/new - Start new meeting
/templates - Summary styles
/my - View meetings
/upgrade - Pro plans
/usage - Your usage

How it works:
1. Upload audio/video or paste transcript
2. Choose summary style
3. Get summary + action items

Prices:
Free: 3 meetings/month
Pro: $14/mo unlimited
Business: $39/mo team features"""
        await update.message.reply_text(help_text)
    
    async def templates_command(self, update, context):
        templates = self.processor.get_templates()
        text = "📝 Summary Templates\n\n"
        
        for key, val in templates.items():
            text += f"• {key}: {val['name']}\n"
        
        text += "\nUse /new to start a meeting!"
        await update.message.reply_text(text)
    
    async def new_meeting(self, update, context):
        """Start new meeting"""
        user = update.effective_user
        
        # Check limits
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        meetings_used = user_data.get("meetings_used", 0) if user_data else 0
        
        if tier == "free" and meetings_used >= 3:
            await update.message.reply_text("❌ Monthly limit reached (3 meetings)\n\nUpgrade to Pro!\n/upgrade")
            return
        
        text = """📹 Start New Meeting

Send me:
• Audio file (MP3, WAV)
• Video file (MP4)
• Or paste transcript text

I'll generate:
• Summary
• Action items
• Key decisions

Default template: standard
Change with: /template [name]"""
        
        self.user_sessions[user.id] = {"step": "waiting_for_content"}
        await update.message.reply_text(text)
    
    async def handle_message(self, update, context):
        text = update.message.text
        user = update.effective_user
        
        if text.startswith("/"):
            return
        
        session = self.user_sessions.get(user.id, {})
        
        if session.get("step") == "waiting_for_content":
            await self.process_meeting(update, context, text)
        else:
            await update.message.reply_text("Use /new to start a new meeting!")
    
    async def handle_document(self, update, context):
        """Handle uploaded audio/video"""
        user = update.effective_user
        
        # Check limits
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        meetings_used = user_data.get("meetings_used", 0) if user_data else 0
        
        if tier == "free" and meetings_used >= 3:
            await update.message.reply_text("❌ Limit reached. Upgrade to Pro!")
            return
        
        file = update.message.document
        await update.message.reply_text(f"📹 Processing {file.file_name}...\nThis may take a minute.")
        
        # In production, download and process file
        await update.message.reply_text("📹 Meeting processed!\n\n" + "Summary would appear here...\n\n" + "Action Items:\n• Follow up on action 1\n• Schedule next meeting")
    
    async def process_meeting(self, update, context, transcript: str):
        user = update.effective_user
        
        await update.message.reply_text("📹 Processing meeting...\nThis takes ~30 seconds.")
        
        try:
            meeting = await self.processor.process_meeting(
                transcript=transcript,
                title=f"Meeting {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            meeting.user_id = user.id
            
            # Save
            self.db.save_meeting(meeting, user.id)
            
            # Send summary
            await context.bot.send_message(
                chat_id=user.id,
                text=f"📹 *Meeting Summary*\n\n"
                     f"*{meeting.title}*\n\n"
                     f"📝 *Summary:*\n{meeting.summary[:500]}...\n\n"
                     f"✅ *Action Items:*\n" + "\n".join([f"• {item}" for item in meeting.action_items[:5]]),
                parse_mode="Markdown"
            )
        
        except Exception as e:
            await context.bot.send_message(chat_id=user.id, text=f"❌ Error: {str(e)}")
    
    async def my_meetings(self, update, context):
        """Show user's meetings"""
        user = update.effective_user
        meetings = self.db.get_user_meetings(user.id, limit=10)
        
        if not meetings:
            await update.message.reply_text("No meetings yet! Use /new to start.")
            return
        
        text = "📹 Your Meetings\n\n"
        for i, m in enumerate(meetings, 1):
            text += f"{i}. {m['title'][:40]}\n"
            text += f"   📅 {m['created'][:10]} | ⏱ {m['duration']}min\n"
        
        await update.message.reply_text(text)
    
    async def upgrade_command(self, update, context):
        text = """💳 Upgrade to Pro

🆓 Free: 3 meetings/month
⭐ Pro ($14/mo): Unlimited + long meetings + priority
🏢 Business ($39/mo): Team features + API + white-label

Reply with "pro" or "business"!"""
        await update.message.reply_text(text)


def run_bot():
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    
    if not CONFIG["telegram_token"]:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = MeetAIBot()
    app = Application.builder().token(CONFIG["telegram_token"]).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("templates", bot.templates_command))
    app.add_handler(CommandHandler("new", bot.new_meeting))
    app.add_handler(CommandHandler("my", bot.my_meetings))
    app.add_handler(CommandHandler("upgrade", bot.upgrade_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, bot.handle_document))
    
    print("📹 MeetAI Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
