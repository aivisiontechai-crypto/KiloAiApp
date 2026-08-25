from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    id: str
    symbol: str
    title: str
    source: str
    sentiment: float
    timestamp: datetime
    url: str = ""


class NewsSentimentEngine:
    def __init__(self) -> None:
        self._news: dict[str, list[NewsItem]] = {}
        self._next_id = 1
        self._sample_headlines = {
            "BTC-USD": [
                ("Bitcoin adoption by institutional investors accelerates", 0.7),
                ("Regulatory concerns weigh on crypto markets", -0.5),
                ("Major ETF inflows boost Bitcoin sentiment", 0.8),
                ("Mining difficulty reaches new all-time high", 0.3),
            ],
            "ETH-USD": [
                ("Ethereum upgrade improves network efficiency", 0.6),
                ("DeFi TVL declines amid market uncertainty", -0.4),
                ("Smart contract adoption grows in enterprise", 0.5),
            ],
        }

    def fetch_news(self, symbol: str, count: int = 5) -> list[NewsItem]:
        headlines = self._sample_headlines.get(symbol, [
            ("Market shows mixed signals for " + symbol, 0.0),
            ("Trading volume increases for " + symbol, 0.2),
            ("Analysts update price targets for " + symbol, 0.1),
        ])
        items = []
        for _ in range(min(count, len(headlines))):
            title, sentiment = random.choice(headlines)
            item = NewsItem(
                id=str(self._next_id),
                symbol=symbol,
                title=title,
                source="MarketNews",
                sentiment=sentiment,
                timestamp=datetime.utcnow(),
            )
            self._next_id += 1
            items.append(item)
        return items

    def get_sentiment_score(self, symbol: str) -> float:
        news = self._news.get(symbol, [])
        if not news:
            return 0.0
        return sum(n.sentiment for n in news) / len(news)

    def get_news(self, symbol: str) -> list[dict]:
        return [
            {
                "id": n.id,
                "title": n.title,
                "source": n.source,
                "sentiment": n.sentiment,
                "timestamp": n.timestamp.isoformat(),
            }
            for n in self._news.get(symbol, [])
        ]
