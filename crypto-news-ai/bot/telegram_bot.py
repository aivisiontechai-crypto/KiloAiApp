#!/usr/bin/env python3
"""
CryptoAI News - Telegram Bot
AI Crypto News with Beautiful UI
"""

import os
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.news_generator import NewsAggregator, NewsDatabase, COIN_KEYWORDS

CONFIG = {"telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "")}


class CryptoNewsBot:
    def __init__(self):
        self.news = NewsAggregator()
        self.db = NewsDatabase()
    
    async def start(self, update, context):
        user = update.effective_user
        self.db.add_user(user.id, user.username or "unknown", "telegram")
        
        welcome = """
╔══════════════════════════════════════╗
║    📰 WELCOME TO CRYPTOAI NEWS 📰   ║
║      AI-Powered Crypto News          ║
╚══════════════════════════════════════╝

📊 Stay informed with AI-curated news
🧠 Smart summaries
💎 Real-time updates
📈 Sentiment analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ *Commands:*

📰 /news - Latest news
🔍 /search [coin] - News for specific coin
💎 /coins - Tracked coins
📈 /sentiment - Market sentiment
❓ /help - More info
"""
        await context.bot.send_message(chat_id=user.id, text=welcome, parse_mode="Markdown")
    
    async def help_command(self, update, context):
        help_text = """
╔══════════════════════════════════════╗
║           📖 HELP & COMMANDS        ║
╚══════════════════════════════════════╝

📰 /news - Get latest crypto news
🔍 /search bitcoin - News for specific coin
💎 /coins - List all tracked coins
📈 /sentiment - Overall market mood
❓ /help - Show this message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *Pricing:*

🆓 Free: 5 news/day
⭐ Pro ($12/mo): Unlimited + alerts
💎 VIP ($24/mo): Early access

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ *Disclaimer:*
News is for informational purposes only.
Not financial advice.
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def news_command(self, update, context, coin: str = None):
        """Get latest news"""
        user = update.effective_user
        
        # Check limits
        user_data = self.db.get_user(user.id)
        tier = user_data.get("tier", "free") if user_data else "free"
        news_used = user_data.get("news_used", 0) if user_data else 0
        
        if tier == "free" and news_used >= 5:
            await update.message.reply_text(
                "❌ *Daily limit reached!* (5 free news)\n\n"
                "💎 Upgrade to Pro for unlimited!\n\n"
                "Use /upgrade to subscribe.",
                parse_mode="Markdown"
            )
            return
        
        await update.message.reply_text("📰 *Fetching latest news...*", parse_mode="Markdown")
        
        try:
            articles = await self.news.get_news(coin)
            
            for article in articles:
                message = self.news.format_news_message(article)
                await context.bot.send_message(chat_id=user.id, text=message, parse_mode="Markdown")
                self.db.save_news(article)
            
            if not articles:
                await context.bot.send_message(chat_id=user.id, text="No news found.")
        
        except Exception as e:
            await context.bot.send_message(chat_id=user.id, text=f"❌ Error: {str(e)}")
    
    async def search_command(self, update, context):
        """Search news for specific coin"""
        text = update.message.text.replace("/search", "").strip().lower()
        
        if not text:
            await update.message.reply_text("Usage: /search bitcoin", parse_mode="Markdown")
            return
        
        # Find matching coin
        matched = None
        for coin in COIN_KEYWORDS:
            if text in coin or text in COIN_KEYWORDS[coin]:
                matched = coin
                break
        
        if matched:
            await self.news_command(update, context, matched)
        else:
            await update.message.reply_text(f"Coin '{text}' not found. Use /coins to see available.", parse_mode="Markdown")
    
    async def coins_command(self, update, context):
        """Show tracked coins"""
        coins = list(COIN_KEYWORDS.keys())
        
        text = "💎 *Tracked Coins:*\n\n"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = []
        row = []
        for i, coin in enumerate(coins):
            row.append(InlineKeyboardButton(f"${coin.upper()}", callback_data=f"news_{coin}"))
            if (i + 1) % 4 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def sentiment_command(self, update, context):
        """Show market sentiment"""
        await update.message.reply_text("📈 *Analyzing market sentiment...*", parse_mode="Markdown")
        
        try:
            articles = await self.news.get_news()
            
            bullish = sum(1 for a in articles if a.sentiment == "bullish")
            bearish = sum(1 for a in articles if a.sentiment == "bearish")
            neutral = len(articles) - bullish - bearish
            
            total = bullish + bearish + neutral or 1
            
            bull_pct = (bullish / total) * 100
            bear_pct = (bearish / total) * 100
            neu_pct = (neutral / total) * 100
            
            # Determine overall mood
            if bull_pct > 60:
                mood = "🐂 BULLISH"
                emoji = "🚀"
            elif bear_pct > 60:
                mood = "🐻 BEARISH"
                emoji = "📉"
            else:
                mood = "⚖️ NEUTRAL"
                emoji = "➡️"
            
            text = f"""
╔══════════════════════════════════════╗
║        📈 MARKET SENTIMENT        ║
╚══════════════════════════════════════╝

{emoji} *Overall:* {mood}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐂 *Bullish:* {bull_pct:.0f}%
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ {bull_pct:.0f}%

🐻 *Bearish:* {bear_pct:.0f}%
▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░ {bear_pct:.0f}%

⚖️ *Neutral:* {neu_pct:.0f}%
▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░ {neu_pct:.0f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📰 Based on {len(articles)} latest articles
"""
            await update.message.reply_text(text, parse_mode="Markdown")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def upgrade_command(self, update, context):
        """Show upgrade options"""
        text = """
╔══════════════════════════════════════╗
║         💎 UPGRADE PLANS 💎        ║
╚══════════════════════════════════════╝

🆓 *Free*
• 5 news per day
• Basic summaries
• Great for trying out!

⭐ *Pro - $12/month*
• Unlimited news
• Real-time alerts
• Priority updates
• All coins tracked

💎 *VIP - $24/month*
• Everything in Pro
• Early access
• Exclusive content
• Private group
• 1-on-1 support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 *Payment via Stripe*

Reply with "pro" or "vip" to upgrade!
"""
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def handle_callback(self, update, context):
        """Handle inline buttons"""
        query = update.callback_query
        await query.answer()
        
        coin = query.data.replace("news_", "")
        await self.news_command(update, context, coin)
    
    async def handle_message(self, update, context):
        """Handle regular messages"""
        await update.message.reply_text("Use /news for latest crypto news!")


def run_bot():
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
    
    if not CONFIG["telegram_token"]:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = CryptoNewsBot()
    app = Application.builder().token(CONFIG["telegram_token"]).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("news", bot.news_command))
    app.add_handler(CommandHandler("search", bot.search_command))
    app.add_handler(CommandHandler("coins", bot.coins_command))
    app.add_handler(CommandHandler("sentiment", bot.sentiment_command))
    app.add_handler(CommandHandler("upgrade", bot.upgrade_command))
    
    app.add_handler(CallbackQueryHandler(bot.handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("📰 CryptoAI News Bot starting...")
    print("💎 Beautiful UI enabled!")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
