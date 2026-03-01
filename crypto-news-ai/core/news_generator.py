#!/usr/bin/env python3
"""
CryptoAI News - Core News Engine
AI-powered crypto news aggregation and summarization
"""

import os
import json
import sqlite3
import asyncio
import uuid
import random
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass


CONFIG = {"openai_api_key": os.getenv("OPENAI_API_KEY", ""), "newsapi_key": os.getenv("NEWSAPI_KEY", "")}


# Coin categories
COIN_KEYWORDS = {
    "bitcoin": ["bitcoin", "btc", "satoshi"],
    "ethereum": ["ethereum", "eth", "vitalik"],
    "solana": ["solana", "sol", "anatomy"],
    "cardano": ["cardano", "ada", "hoskinson"],
    "polkadot": ["polkadot", "dot", "gavin wood"],
    "ripple": ["ripple", "xrp", "brad"],
    "chainlink": ["chainlink", "link", "sergey"],
    "polygon": ["polygon", "matic", "jay"],
    "uniswap": ["uniswap", "uni", " Hayden"],
    "avalanche": ["avalanche", "avax", "eminence"],
}


class SentimentAnalyzer:
    """Analyze sentiment of news"""
    
    positive_words = ["bullish", "surge", "rally", "gain", "soar", "up", "high", "breakout", "growth", "adoption", "partnership", "launch", "upgrade", "positive"]
    negative_words = ["bearish", "crash", "drop", "fall", "down", "low", "breakdown", "hack", "scam", "ban", "regulation", "lawsuit", "concern", "warning", "negative"]
    
    def analyze(self, text: str) -> Dict:
        text_lower = text.lower()
        
        pos_count = sum(1 for word in self.positive_words if word in text_lower)
        neg_count = sum(1 for word in self.negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "bullish"
            emoji = "🐂"
            score = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
        elif neg_count > pos_count:
            sentiment = "bearish"
            emoji = "🐻"
            score = min(0.9, 0.5 + (neg_count - pos_count) * 0.1)
        else:
            sentiment = "neutral"
            emoji = "⚖️"
            score = 0.5
        
        return {"sentiment": sentiment, "emoji": emoji, "score": score}


@dataclass
class NewsArticle:
    id: str
    title: str
    source: str
    url: str
    published_at: str
    summary: str
    sentiment: str
    sentiment_emoji: str
    sentiment_score: float
    related_coins: List[str]
    created_at: str


class NewsAggregator:
    """Aggregate crypto news from various sources"""
    
    def __init__(self):
        self.sentiment = SentimentAnalyzer()
        self.coin_keywords = COIN_KEYWORDS
    
    async def fetch_news(self, coin: str = None) -> List[Dict]:
        """Fetch news articles"""
        
        # Mock news for demo
        mock_news = [
            {
                "title": "Bitcoin Surges Past $100K as Institutional Adoption Accelerates",
                "source": "CoinDesk",
                "url": "https://coindesk.com/bitcoin-surge",
                "published_at": datetime.now().isoformat(),
                "content": "Bitcoin has broken through the $100,000 barrier for the first time...",
            },
            {
                "title": "Ethereum Foundation Announces Major Protocol Upgrade",
                "source": "The Block",
                "url": "https://theblock.eth-upgrade",
                "published_at": datetime.now().isoformat(),
                "content": "The Ethereum Foundation has announced plans for a major upgrade...",
            },
            {
                "title": "SEC Delays Bitcoin ETF Decision Again",
                "source": "Reuters",
                "url": "https://reuters.com/sec-delay",
                "published_at": datetime.now().isoformat(),
                "content": "The SEC has once again delayed its decision on the Bitcoin ETF...",
            },
            {
                "title": "Solana DeFi TVL Reaches All-Time High",
                "source": "DeFi Pulse",
                "url": "https://defipulse.solana",
                "published_at": datetime.now().isoformat(),
                "content": "Solana's total value locked has reached a new all-time high...",
            },
            {
                "title": "Major Exchange Reports $500M in Daily Trading Volume",
                "source": "Bloomberg",
                "url": "https://bloomberg.exchange-volume",
                "published_at": datetime.now().isoformat(),
                "content": "Leading cryptocurrency exchange reports record trading volumes...",
            },
            {
                "title": "New Regulatory Framework Proposed for Crypto in EU",
                "source": "Financial Times",
                "url": "https://ft.eu-crypto-reg",
                "published_at": datetime.now().isoformat(),
                "content": "European regulators have proposed a comprehensive new framework...",
            },
            {
                "title": "DeFi Protocol Hack Results in $50M Loss",
                "source": "CryptoSlate",
                "url": "https://cryptoslate.hack",
                "published_at": datetime.now().isoformat(),
                "content": "A decentralized finance protocol has been exploited...",
            },
            {
                "title": "Major Bank Announces Crypto Custody Service",
                "source": "Wall Street Journal",
                "url": "https://wsj.bank-crypto",
                "published_at": datetime.now().isoformat(),
                "content": "One of the world's largest banks has announced plans...",
            },
        ]
        
        # Filter by coin if specified
        if coin:
            coin_lower = coin.lower()
            keywords = self.coin_keywords.get(coin_lower, [coin_lower])
            filtered = []
            for news in mock_news:
                content = (news["title"] + " " + news["content"]).lower()
                if any(kw in content for kw in keywords):
                    filtered.append(news)
            return filtered[:5] if filtered else mock_news[:3]
        
        return mock_news[:5]
    
    async def generate_summary(self, title: str, content: str) -> str:
        """Generate AI summary of article"""
        
        if not CONFIG["openai_api_key"]:
            # Fallback summary
            return content[:200] + "..." if len(content) > 200 else content
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Summarize this crypto news article in 2-3 sentences. Be concise and informative."},
                    {"role": "user", "content": f"Title: {title}\n\nContent: {content[:2000]}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        
        except:
            return content[:200] + "..."
    
    async def get_news(self, coin: str = None) -> List[NewsArticle]:
        """Get processed news articles"""
        
        articles = await self.fetch_news(coin)
        results = []
        
        for article in articles:
            # Analyze sentiment
            text = article["title"] + " " + article.get("content", "")
            sentiment_data = self.sentiment.analyze(text)
            
            # Generate summary
            summary = await self.generate_summary(article["title"], article.get("content", ""))
            
            # Find related coins
            related = []
            for coin_name, keywords in self.coin_keywords.items():
                if any(kw in text.lower() for kw in keywords):
                    related.append(coin_name.upper())
            
            news = NewsArticle(
                id=str(uuid.uuid4())[:8],
                title=article["title"],
                source=article["source"],
                url=article["url"],
                published_at=article["published_at"],
                summary=summary,
                sentiment=sentiment_data["sentiment"],
                sentiment_emoji=sentiment_data["emoji"],
                sentiment_score=sentiment_data["score"],
                related_coins=related,
                created_at=datetime.now().isoformat()
            )
            results.append(news)
        
        return results
    
    def format_news_message(self, article: NewsArticle) -> str:
        """Format news as beautiful Telegram message"""
        
        # Time ago
        try:
            published = datetime.fromisoformat(article.published_at)
            now = datetime.now()
            diff = (now - published).total_seconds()
            
            if diff < 3600:
                time_ago = f"{int(diff/60)}m ago"
            elif diff < 86400:
                time_ago = f"{int(diff/3600)}h ago"
            else:
                time_ago = f"{int(diff/86400)}d ago"
        except:
            time_ago = "recently"
        
        coins_text = " ".join([f"${c}" for c in article.related_coins]) if article.related_coins else "$GENERAL"
        
        message = f"""
╔══════════════════════════════════════╗
║         📰 CRYPTO NEWS 📰          ║
╚══════════════════════════════════════╝

{article.sentiment_emoji} *{article.sentiment.upper()}* {article.sentiment_emoji}

📰 *{article.title}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 *Summary:*
_{article.summary}_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️ *Coins:* {coins_text}
📡 *Source:* {article.source}
⏰ * {time_ago}

🔗 [Read More]({article.url})

🎫 *{article.id}*
╚══════════════════════════════════════╝
"""
        return message


class NewsDatabase:
    def __init__(self, db_path: str = "data/crypto_news.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, platform TEXT, tier TEXT DEFAULT 'free',
            news_used INTEGER DEFAULT 0, subscription_expires TEXT, lifetime_spent REAL DEFAULT 0, created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY, title TEXT, source TEXT, url TEXT, published_at TEXT,
            summary TEXT, sentiment TEXT, sentiment_score REAL, related_coins TEXT,
            created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, plan TEXT,
            stripe_payment_id TEXT, created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER, coin TEXT, added_at TEXT, PRIMARY KEY (user_id, coin))''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str, platform: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (user_id, username, platform, created_at) VALUES (?, ?, ?, ?)',
            (user_id, username, platform, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {"user_id": row[0], "username": row[1], "platform": row[2], "tier": row[3],
                    "news_used": row[4], "subscription_expires": row[5], "lifetime_spent": row[6], "created_at": row[7]}
        return None
    
    def save_news(self, article: NewsArticle):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO news (id, title, source, url, published_at, summary, sentiment, sentiment_score, related_coins, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (article.id, article.title, article.source, article.url, article.published_at,
             article.summary, article.sentiment, article.sentiment_score, ",".join(article.related_coins), article.created_at))
        conn.commit()
        conn.close()
    
    def get_recent_news(self, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM news ORDER BY published_at DESC LIMIT ?', (limit,))
        news = []
        for row in c.fetchall():
            news.append({
                "id": row[0], "title": row[1], "source": row[2], "url": row[3],
                "published_at": row[4], "summary": row[5], "sentiment": row[6],
                "sentiment_score": row[7], "related_coins": row[8].split(",") if row[8] else []
            })
        conn.close()
        return news


if __name__ == "__main__":
    agg = NewsAggregator()
    print("📰 CryptoAI News Ready")
    print("\nCoin categories:")
    for coin in list(COIN_KEYWORDS.keys())[:5]:
        print(f"  {coin}")
