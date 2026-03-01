#!/usr/bin/env python3
"""
SignalAI - Telegram Bot
AI Crypto Trading Signals with Beautiful UI
Using OpenRouter API
"""

import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.signal_generator import SignalGenerator, SignalDatabase, CryptoDataProvider

# Use OpenRouter!
CONFIG = {"telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "")}


class SignalAIBot:
    def __init__(self):
        self.generator = SignalGenerator()
        self.crypto = CryptoDataProvider()
        self.db = SignalDatabase()
        self.user_sessions = {}
    
    async def start(self, update, context):
        user = update.effective_user
        self.db.add_user(user.id, user.username or "unknown", "telegram")
        
        welcome = """
╔══════════════════════════════════════╗
║    🚀 WELCOME TO SIGNALAI 🚀       
║     AI Crypto Trading Signals      
╚══════════════════════════════════════╝

📈 Get real-time trading signals
🎯 Entry, target & stop-loss prices
🧠 AI-powered market analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ *Available Commands:*

🆕 /signal - Get a new signal
📊 /coins - List tracked coins
👀 /watchlist - Your watchlist
📈 /signals - Recent signals
💎 /upgrade - Premium plans
❓ /help - More info
"""
        await context.bot.send_message(chat_id=user.id, text=welcome, parse_mode="Markdown")
    
    async def help_command(self, update, context):
        help_text = """
╔══════════════════════════════════════╗
║          📖 HELP & COMMANDS         
╚══════════════════════════════════════╝

🆕 /signal - Get a new trading signal
📊 /coins - View all tracked coins
👀 /watchlist - Manage your watchlist
📈 /signals - View recent signals
💎 /upgrade - Premium subscription
❓ /help - Show this message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *Pricing:*

🆓 Free: 3 signals/week
⭐ Pro ($19/mo): Daily signals + alerts
💎 VIP ($49/mo): Early signals + private group

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ *Disclaimer:*
Trading involves risk. Signals are for educational purposes only.
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def signal_command(self, update, context):
        user = update.effective_user
        
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        signals_used = user_data.get("signals_used", 0) if user_data else 0
        
        if tier == "free" and signals_used >= 3:
            await update.message.reply_text(
                "❌ *Weekly limit reached!* (3 free signals)\n\n💎 Upgrade to Pro!\n/upgrade",
                parse_mode="Markdown"
            )
            return
        
        coins = self.generator.get_coins()
        
        text = "📊 *Select a Coin:*\n\n"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = []
        row = []
        for i, coin in enumerate(coins):
            row.append(InlineKeyboardButton(f"{coin['symbol']}", callback_data=f"coin_{coin['id']}"))
            if (i + 1) % 3 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🎲 Random Coin", callback_data="coin_random")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def handle_callback(self, update, context):
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        coin_id = query.data.replace("coin_", "")
        
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        signals_used = user_data.get("signals_used", 0) if user_data else 0
        
        if tier == "free" and signals_used >= 3:
            await query.edit_message_text("❌ Limit reached! Upgrade to Pro.")
            return
        
        if coin_id == "random":
            import random
            coins = self.generator.get_coins()
            coin_id = random.choice(coins)["id"]
        
        await query.edit_message_text("🎯 *Generating signal...*\n\nPlease wait...", parse_mode="Markdown")
        
        try:
            signal = await self.generator.generate_signal(coin_id)
            self.db.save_signal(signal)
            
            message = self.generator.format_signal_message(signal)
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("🔄 New Signal", callback_data="new_signal")],
                [InlineKeyboardButton("👀 Add to Watchlist", callback_data=f"watch_{coin_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(chat_id=user.id, text=message, parse_mode="Markdown", reply_markup=reply_markup)
        
        except Exception as e:
            await context.bot.send_message(chat_id=user.id, text=f"❌ Error: {str(e)}")
    
    async def coins_command(self, update, context):
        coins = self.generator.get_coins()
        
        text = "📊 *Tracked Coins:*\n\n"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = []
        row = []
        for i, coin in enumerate(coins):
            row.append(InlineKeyboardButton(f"${coin['symbol']}", callback_data=f"coin_{coin['id']}"))
            if (i + 1) % 4 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def signals_command(self, update, context):
        signals = self.db.get_recent_signals(limit=5)
        
        if not signals:
            await update.message.reply_text("No signals yet! Use /signal to get one.")
            return
        
        text = "📈 *Recent Signals:*\n\n"
        
        for s in signals:
            emoji = "🟢" if "BUY" in s["signal_type"] else "🔴" if "SELL" in s["signal_type"] else "🟡"
            text += f"{emoji} *{s['symbol']}* {s['signal_type']}\n"
            text += f"   Entry: ${s['entry_price']:,.2f} → Target: ${s['target_price']:,.2f}\n\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def watchlist_command(self, update, context):
        text = """
👀 *Your Watchlist:*

You haven't added any coins yet!

Use /signal to get a signal!
"""
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def upgrade_command(self, update, context):
        text = """
╔══════════════════════════════════════╗
║         💎 UPGRADE PLANS 💎         
╚══════════════════════════════════════╝

🆓 *Free*
• 3 signals per week
• Basic signals

⭐ *Pro - $19/month*
• Unlimited signals
• Daily market analysis

💎 *VIP - $49/month*
• Everything in Pro
• Early signals
• Private group
"""
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def handle_message(self, update, context):
        await update.message.reply_text("Use /signal to get a trading signal!")


def run_bot():
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
    
    if not CONFIG["telegram_token"]:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = SignalAIBot()
    app = Application.builder().token(CONFIG["telegram_token"]).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("signal", bot.signal_command))
    app.add_handler(CommandHandler("coins", bot.coins_command))
    app.add_handler(CommandHandler("signals", bot.signals_command))
    app.add_handler(CommandHandler("watchlist", bot.watchlist_command))
    app.add_handler(CommandHandler("upgrade", bot.upgrade_command))
    
    app.add_handler(CallbackQueryHandler(bot.handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("📈 SignalAI Bot starting... (OpenRouter)")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
