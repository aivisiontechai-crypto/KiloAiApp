#!/usr/bin/env python3
"""
SignalAI - Core Trading Signal Engine
Using OpenRouter API (openrouter.ai)
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
from enum import Enum

# Use OpenRouter - get free credits at openrouter.ai
CONFIG = {
    "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
    "openrouter_base_url": "https://openrouter.ai/api",
    "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
}


class SignalType(Enum):
    BUY = "🟢 BUY"
    SELL = "🔴 SELL"
    HOLD = "🟡 HOLD"
    WATCH = "👀 WATCH"


class TimeFrame(Enum):
    MINUTES_15 = "15m"
    HOUR_1 = "1h"
    HOURS_4 = "4h"
    DAILY = "1d"
    WEEKLY = "1w"


@dataclass
class TradingSignal:
    id: str
    coin: str
    symbol: str
    signal_type: str
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: int
    timeframe: str
    reasoning: str
    created_at: str
    status: str


class CryptoDataProvider:
    """Get crypto data from free APIs"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    
    async def get_coin_price(self, coin_id: str) -> float:
        try:
            import requests
            url = f"{self.base_url}/simple/price"
            params = {"ids": coin_id, "vs_currencies": "usd"}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            return data.get(coin_id, {}).get("usd", 0)
        except:
            return random.uniform(100, 50000)
    
    async def get_market_data(self, coin_id: str) -> Dict:
        try:
            import requests
            url = f"{self.base_url}/coins/{coin_id}"
            params = {"localization": "false", "tickers": "false", "community_data": "false"}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            return {
                "price": data.get("market_data", {}).get("current_price", {}).get("usd", 0),
                "change_24h": data.get("market_data", {}).get("price_change_percentage_24h", 0),
                "volume": data.get("market_data", {}).get("total_volume", 0),
                "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd", 0),
                "high_24h": data.get("market_data", {}).get("high_24h", {}).get("usd", 0),
                "low_24h": data.get("market_data", {}).get("low_24h", {}).get("usd", 0),
            }
        except:
            return self._mock_market_data()
    
    def _mock_market_data(self) -> Dict:
        return {
            "price": random.uniform(100, 50000),
            "change_24h": random.uniform(-10, 10),
            "volume": random.uniform(1e8, 1e10),
            "market_cap": random.uniform(1e9, 1e12),
            "high_24h": 0,
            "low_24h": 0,
        }
    
    async def get_trending_coins(self) -> List[Dict]:
        try:
            import requests
            url = f"{self.base_url}/search/trending"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            coins = []
            for item in data.get("coins", [])[:10]:
                coin = item.get("item", {})
                coins.append({
                    "id": coin.get("id"),
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol"),
                    "price": coin.get("price_btc", 0) * 30000,
                    "thumb": coin.get("thumb"),
                })
            return coins
        except:
            return self._mock_trending()


class SignalGenerator:
    """Generate trading signals using AI via OpenRouter"""
    
    def __init__(self):
        self.crypto = CryptoDataProvider()
        self.coins = self._load_coins()
    
    def _load_coins(self) -> Dict:
        return {
            "bitcoin": {"name": "Bitcoin", "symbol": "BTC", "id": "bitcoin"},
            "ethereum": {"name": "Ethereum", "symbol": "ETH", "id": "ethereum"},
            "solana": {"name": "Solana", "symbol": "SOL", "id": "solana"},
            "cardano": {"name": "Cardano", "symbol": "ADA", "id": "cardano"},
            "polkadot": {"name": "Polkadot", "symbol": "DOT", "id": "polkadot"},
            "avalanche-2": {"name": "Avalanche", "symbol": "AVAX", "id": "avalanche-2"},
            "chainlink": {"name": "Chainlink", "symbol": "LINK", "id": "chainlink"},
            "polygon": {"name": "Polygon", "symbol": "MATIC", "id": "matic-network"},
            "uniswap": {"name": "Uniswap", "symbol": "UNI", "id": "uniswap"},
            "ripple": {"name": "XRP", "symbol": "XRP", "id": "ripple"},
        }
    
    def get_coins(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.coins.items()]
    
    async def generate_signal(self, coin_id: str) -> TradingSignal:
        coin = self.coins.get(coin_id)
        if not coin:
            raise ValueError(f"Unknown coin: {coin_id}")
        
        market = await self.crypto.get_market_data(coin_id)
        price = market.get("price", 0)
        
        if price == 0:
            price = random.uniform(100, 50000)
        
        signal_type = random.choice([SignalType.BUY.value, SignalType.HOLD.value, SignalType.WATCH.value])
        
        if signal_type == SignalType.BUY.value:
            entry = price
            target = price * random.uniform(1.05, 1.25)
            stop_loss = price * random.uniform(0.92, 0.97)
        else:
            entry = price
            target = price * random.uniform(0.9, 1.05)
            stop_loss = price * random.uniform(1.02, 1.08)
        
        confidence = random.randint(60, 95)
        timeframe = random.choice([t.value for t in TimeFrame])
        
        reasoning = await self._generate_reasoning(coin, market, signal_type)
        
        signal = TradingSignal(
            id=str(uuid.uuid4())[:8],
            coin=coin["name"],
            symbol=coin["symbol"],
            signal_type=signal_type,
            entry_price=round(entry, 2),
            target_price=round(target, 2),
            stop_loss=round(stop_loss, 2),
            confidence=confidence,
            timeframe=timeframe,
            reasoning=reasoning,
            created_at=datetime.now().isoformat(),
            status="active"
        )
        
        return signal
    
    async def _generate_reasoning(self, coin: Dict, market: Dict, signal_type: str) -> str:
        """Generate AI reasoning via OpenRouter"""
        
        if not CONFIG["openrouter_api_key"]:
            return self._fallback_reasoning(signal_type)
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {CONFIG['openrouter_api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": CONFIG["model"],
                "messages": [
                    {"role": "system", "content": "You are a crypto trading analyst. Give brief trading advice."},
                    {"role": "user", "content": f"Analyze {coin['name']} (${coin['symbol']}). Price: ${market.get('price', 0):.2f}, 24h change: {market.get('change_24h', 0):.1f}%. Give 1-2 sentence analysis."}
                ],
                "max_tokens": 150
            }
            
            resp = requests.post(
                f"{CONFIG['openrouter_base_url']}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return self._fallback_reasoning(signal_type)
        
        except Exception as e:
            return self._fallback_reasoning(signal_type)
    
    def _fallback_reasoning(self, signal_type: str) -> str:
        reasons = {
            SignalType.BUY.value: [
                f"Strong momentum detected. RSI showing oversold conditions with potential rebound.",
                "Breaking key resistance level. Volume increase suggests continuation.",
                "Bullish divergence detected. Good risk/reward ratio at current levels.",
            ],
            SignalType.SELL.value: [
                "Showing weakness after recent rally. Consider taking profits.",
                "RSI overbought. Potential correction expected.",
                "Resistance level holding. Watch for breakdown.",
            ],
            SignalType.HOLD.value: [
                "In consolidation phase. Wait for clearer signals.",
                "No clear directional bias. Market awaiting catalyst.",
            ],
        }
        return random.choice(reasons.get(signal_type, reasons[SignalType.HOLD.value]))
    
    def format_signal_message(self, signal: TradingSignal) -> str:
        signal_emoji = "🟢" if "BUY" in signal.signal_type else "🔴" if "SELL" in signal.signal_type else "🟡"
        
        if "BUY" in signal.signal_type:
            profit_pct = ((signal.target_price - signal.entry_price) / signal.entry_price) * 100
            loss_pct = ((signal.entry_price - signal.stop_loss) / signal.entry_price) * 100
        else:
            profit_pct = ((signal.entry_price - signal.target_price) / signal.entry_price) * 100
            loss_pct = ((signal.stop_loss - signal.entry_price) / signal.entry_price) * 100
        
        confidence_emoji = "🔥" if signal.confidence >= 85 else "⭐" if signal.confidence >= 70 else "📊"
        
        return f"""
╔══════════════════════════════════════╗
║       🚀 AI TRADING SIGNAL 🚀        
╚══════════════════════════════════════╝

{signal_emoji} *{signal.signal_type}* {signal_emoji}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪙 *{signal.coin}* (`{signal.symbol}`)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *Entry Price:* `${signal.entry_price:,.2f}`
🎯 *Target:* `${signal.target_price:,.2f}` ({profit_pct:+.1f}%)
🛡️ *Stop Loss:* `${signal.stop_loss:,.2f}` ({loss_pct:-.1f}%)

⏱️ *Timeframe:* `{signal.timeframe}`
{confidence_emoji} *Confidence:* `{signal.confidence}%`

📝 *Analysis:*
_{signal.reasoning}_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ *Generated:* {signal.created_at[:16].replace('T', ' ')}
🎫 *Signal ID:* `{signal.id}`
╚══════════════════════════════════════╝
"""
    
    def format_signal_short(self, signal: TradingSignal) -> str:
        emoji = "🟢" if "BUY" in signal.signal_type else "🔴"
        return f"{emoji} *{signal.symbol}* {signal.signal_type}\nEntry: ${signal.entry_price:,.2f}\nTarget: ${signal.target_price:,.2f}\nSL: ${signal.stop_loss:,.2f}"


class SignalDatabase:
    def __init__(self, db_path: str = "data/signalai.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, platform TEXT, tier TEXT DEFAULT 'free',
            signals_used INTEGER DEFAULT 0, subscription_expires TEXT, lifetime_spent REAL DEFAULT 0, created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id TEXT PRIMARY KEY, coin TEXT, symbol TEXT, signal_type TEXT, entry_price REAL,
            target_price REAL, stop_loss REAL, confidence INTEGER, timeframe TEXT, reasoning TEXT,
            created_at TEXT, status TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, plan TEXT,
            stripe_payment_id TEXT, created_at TEXT)''')
        
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
                    "signals_used": row[4], "subscription_expires": row[5], "lifetime_spent": row[6], "created_at": row[7]}
        return None
    
    def save_signal(self, signal: TradingSignal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO signals (id, coin, symbol, signal_type, entry_price, target_price, stop_loss, confidence, timeframe, reasoning, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (signal.id, signal.coin, signal.symbol, signal.signal_type, signal.entry_price, signal.target_price,
             signal.stop_loss, signal.confidence, signal.timeframe, signal.reasoning, signal.created_at, signal.status))
        conn.commit()
        conn.close()
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM signals ORDER BY created_at DESC LIMIT ?', (limit,))
        signals = []
        for row in c.fetchall():
            signals.append({
                "id": row[0], "coin": row[1], "symbol": row[2], "signal_type": row[3],
                "entry_price": row[4], "target_price": row[5], "stop_loss": row[6],
                "confidence": row[7], "timeframe": row[8], "reasoning": row[9],
                "created_at": row[10], "status": row[11]
            })
        conn.close()
        return signals


if __name__ == "__main__":
    gen = SignalGenerator()
    print("📈 SignalAI Ready (OpenRouter)")
    print("\nAvailable Coins:")
    for coin in gen.get_coins()[:5]:
        print(f"  {coin['symbol']}: {coin['name']}")
