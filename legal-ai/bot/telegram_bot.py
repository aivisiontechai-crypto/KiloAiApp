#!/usr/bin/env python3
"""
LegalAI - Telegram Bot
AI Legal Document Assistant
"""

import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.document_generator import LegalDocumentGenerator, DocumentDatabase

CONFIG = {"telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "")}


class LegalAIBot:
    def __init__(self):
        self.generator = LegalDocumentGenerator()
        self.db = DocumentDatabase()
        self.user_sessions = {}
    
    async def start(self, update, context):
        user = update.effective_user
        self.db.add_user(user.id, user.username or "unknown", "telegram")
        
        welcome = """⚖️ Welcome to LegalAI

Your AI-powered legal document assistant.

I can generate:
• NDA
• Service Contract
• Privacy Policy
• Terms of Service
• Employment Contract
• Demand Letter
• Invoice
• LLC Agreement

Choose a document type to get started!

/documents - List all types
/upgrade - Subscribe to Pro
/help - More info"""
        await context.bot.send_message(chat_id=user.id, text=welcome)
    
    async def help_command(self, update, context):
        help_text = """⚖️ LegalAI Help

/howitworks:
1. Choose document type
2. Answer a few questions
3. Get your document!

Plans:
Free: 1 doc/month
Pro: $29/mo unlimited
Business: $99/mo custom templates

/documents - See all types
/upgrade - Subscribe"""
        await update.message.reply_text(help_text)
    
    async def list_documents(self, update, context):
        docs = self.generator.get_available_docs()
        text = "📄 Available Documents:\n\n"
        for doc in docs:
            text += f"• {doc['name']} - ${doc['price']}\n"
        await update.message.reply_text(text)
    
    async def show_subscription(self, update, context):
        text = """💳 Subscription Plans

Free: 1 document/month
Pro ($29/mo): Unlimited + all types
Business ($99/mo): Custom templates + API

Type /upgrade to subscribe!"""
        await update.message.reply_text(text)
    
    async def handle_message(self, update, context):
        text = update.message.text
        user = update.effective_user
        
        # Check for document selection
        doc_types = {"1": "nda", "2": "service_contract", "3": "privacy_policy", "4": "terms_of_service",
                     "5": "employment", "6": "demand_letter", "7": "invoice", "8": "llc"}
        
        if text in doc_types:
            await self.create_document(update, context, doc_types[text])
        elif text.startswith("/"):
            # Command
            pass
        else:
            await update.message.reply_text("Welcome! Use /documents to see available types, then reply with the number.")
    
    async def create_document(self, update, context, doc_type: str):
        user = update.effective_user
        template = self.generator.doc_templates.get(doc_type)
        
        if not template:
            await update.message.reply_text("❌ Invalid document type")
            return
        
        # Check subscription
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        docs_used = user_data.get("documents_used", 0) if user_data else 0
        
        if tier == "free" and docs_used >= 1:
            await update.message.reply_text("❌ Free limit reached (1 doc/month). Upgrade to Pro for unlimited!")
            return
        
        # Ask for variables
        variables_needed = template["variables"]
        self.user_sessions[user.id] = {"doc_type": doc_type, "variables": {}, "step": 0, "needed": variables_needed}
        
        first_var = variables_needed[0].replace("_", " ").title()
        await update.message.reply_text(f"📝 Creating: {template['name']}\n\nWhat is the *{first_var}*?")


def run_bot():
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    
    if not CONFIG["telegram_token"]:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = LegalAIBot()
    app = Application.builder().token(CONFIG["telegram_token"]).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("documents", bot.list_documents))
    app.add_handler(CommandHandler("upgrade", bot.show_subscription))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("⚖️ LegalAI Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
