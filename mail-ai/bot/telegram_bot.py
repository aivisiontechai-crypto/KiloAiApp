#!/usr/bin/env python3
"""
MailAI - Telegram Bot
AI Email Generator
"""

import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.email_generator import EmailGenerator, EmailDatabase, EMAIL_TYPES, TONES, LANGUAGES

CONFIG = {"telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "")}


class MailAIBot:
    def __init__(self):
        self.generator = EmailGenerator()
        self.db = EmailDatabase()
        self.user_sessions = {}
    
    async def start(self, update, context):
        user = update.effective_user
        self.db.add_user(user.id, user.username or "unknown", "telegram")
        
        welcome = """📧 Welcome to MailAI

Your AI-powered email assistant!

I can write:
• Replies to emails
• Cold outreach
• Follow-ups
• Meeting requests
• Thank you notes
• Introductions

Get started:
/write - Create email
/types - View email types
/tones - View tones
/my - Your emails
/upgrade - Subscribe
/help - More info"""
        await context.bot.send_message(chat_id=user.id, text=welcome)
    
    async def help_command(self, update, context):
        help_text = """📧 MailAI Help

/write - Start writing an email
/types - Available email types
/tones - Writing tones
/my - View your emails
/upgrade - Pro plans
/usage - Your usage

Prices:
Free: 5 emails/week
Pro: $9/mo unlimited
Business: $29/mo team features"""
        await update.message.reply_text(help_text)
    
    async def types_command(self, update, context):
        types = self.generator.get_email_types()
        text = "📧 Email Types\n\n"
        
        for key, val in types.items():
            text += f"• {key}: {val['name']}\n"
        
        text += "\nUse /write to create one!"
        await update.message.reply_text(text)
    
    async def tones_command(self, update, context):
        tones = self.generator.get_tones()
        text = "🎨 Writing Tones\n\n"
        
        for key, val in tones.items():
            text += f"• {key}: {val}\n"
        
        text += "\nDefault: professional"
        await update.message.reply_text(text)
    
    async def write_command(self, update, context):
        """Start email creation"""
        user = update.effective_user
        
        # Check limits
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        emails_used = user_data.get("emails_used", 0) if user_data else 0
        
        if tier == "free" and emails_used >= 5:
            await update.message.reply_text("❌ Weekly limit reached (5 emails)\n\nUpgrade to Pro!\n/upgrade")
            return
        
        types = self.generator.get_email_types()
        text = "📧 Create Email\n\nChoose type:\n\n"
        
        for i, (key, val) in enumerate(types.items(), 1):
            text += f"{i}. {val['name']}\n"
        
        text += "\nReply with the number (1-6)"
        
        self.user_sessions[user.id] = {"step": "choose_type"}
        await update.message.reply_text(text)
    
    async def handle_message(self, update, context):
        text = update.message.text
        user = update.effective_user
        
        session = self.user_sessions.get(user.id, {})
        
        if session.get("step") == "choose_type":
            await self.handle_type_selection(update, context, text)
        elif session.get("step") == "enter_subject":
            await self.handle_subject(update, context, text)
        elif session.get("step") == "enter_email":
            await self.handle_email_content(update, context, text)
        else:
            await update.message.reply_text("Use /write to create an email!")
    
    async def handle_type_selection(self, update, context, selection: str):
        user = update.effective_user
        
        types_list = list(EMAIL_TYPES.keys())
        
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(types_list):
                email_type = types_list[idx]
                self.user_sessions[user.id] = {"step": "enter_subject", "email_type": email_type}
                
                await update.message.reply_text(
                    f"📧 Type: {EMAIL_TYPES[email_type]['name']}\n\n"
                    f"What's the subject of the email you're replying to or writing about?"
                )
            else:
                await update.message.reply_text("Invalid selection. Use /write to try again.")
        except ValueError:
            await update.message.reply_text("Please enter a number. Use /write to try again.")
    
    async def handle_subject(self, update, context, subject: str):
        user = update.effective_user
        
        self.user_sessions[user.id]["subject"] = subject
        self.user_sessions[user.id]["step"] = "enter_email"
        
        await update.message.reply_text(
            "📧 Now paste the original email (or describe what you want to say)\n\n"
            "Or just describe what you want the email to be about."
        )
    
    async def handle_email_content(self, update, context, content: str):
        user = update.effective_user
        
        session = self.user_sessions[user.id]
        email_type = session.get("email_type", "reply")
        subject = session.get("subject", "No Subject")
        
        await update.message.reply_text("✍️ Writing your email...\nThis takes a few seconds.")
        
        try:
            generated = await self.generator.generate_email(
                email_type=email_type,
                subject=subject,
                original_email=content,
                tone="professional",
                language="en"
            )
            
            # Save
            email_req = EmailRequest(
                id=str(uuid.uuid4())[:8],
                user_id=user.id,
                email_type=email_type,
                subject=subject,
                original_email=content,
                generated_email=generated,
                tone="professional",
                language="en",
                created_at=datetime.now().isoformat(),
                status="completed"
            )
            self.db.save_email(email_req)
            
            # Send email
            await context.bot.send_message(
                chat_id=user.id,
                text=f"✍️ *Your Email*\n\n{generated}",
                parse_mode="Markdown"
            )
            
            await context.bot.send_message(
                chat_id=user.id,
                text="✅ Email saved! Use /my to view history."
            )
        
        except Exception as e:
            await context.bot.send_message(chat_id=user.id, text=f"❌ Error: {str(e)}")
        
        # Clear session
        self.user_sessions.pop(user.id, None)
    
    async def my_emails(self, update, context):
        """Show user's emails"""
        user = update.effective_user
        emails = self.db.get_user_emails(user.id, limit=10)
        
        if not emails:
            await update.message.reply_text("No emails yet! Use /write to create one.")
            return
        
        text = "📧 Your Emails\n\n"
        for i, e in enumerate(emails, 1):
            text += f"{i}. [{e['type']}] {e['subject'][:30]}...\n"
            text += f"   Tone: {e['tone']} | {e['created'][:10]}\n"
        
        await update.message.reply_text(text)
    
    async def upgrade_command(self, update, context):
        text = """💳 Upgrade to Pro

🆓 Free: 5 emails/week
⭐ Pro ($9/mo): Unlimited + custom tones + priority
🏢 Business ($29/mo): Team features + templates

Reply with "pro" or "business"!"""
        await update.message.reply_text(text)


def run_bot():
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    
    if not CONFIG["telegram_token"]:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = MailAIBot()
    app = Application.builder().token(CONFIG["telegram_token"]).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("types", bot.types_command))
    app.add_handler(CommandHandler("tones", bot.tones_command))
    app.add_handler(CommandHandler("write", bot.write_command))
    app.add_handler(CommandHandler("my", bot.my_emails))
    app.add_handler(CommandHandler("upgrade", bot.upgrade_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("📧 MailAI Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
