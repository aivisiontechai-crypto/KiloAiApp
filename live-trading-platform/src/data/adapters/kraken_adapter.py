from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable, Optional

from src.data.models import AssetClass, Candle, OrderBook, OrderBookLevel, Price

logger = logging.getLogger(__name__)


class KrakenAdapter(BaseDataAdapter):
    asset_class = AssetClass.CRYPTO
    base_url = "https://api.kraken.com/0/public"

    def __init__(self, symbols: list[str]):
        self.symbols = [self.map_symbol(s) for s in symbols]

    def map_symbol(self, symbol: str) -> str:
        if symbol.upper() == "BTC-USD":
            return "XBTUSD"
        return symbol.replace("-", "").upper()

    def unmap_symbol(self, symbol: str) -> str:
        if symbol.upper() == "XBTUSD":
            return "BTC-USD"
        return symbol

    async def connect(self) -> None:
        logger.info("Kraken adapter connected")

    async def disconnect(self) -> None:
        logger.info("Kraken adapter disconnected")

    async def get_historical_candles(self, symbol: str, limit: int = 100) -> list[Candle]:
        mapped = self.map_symbol(symbol)
        pair = urllib.parse.quote(mapped)
        url = f"{self.base_url}/OHLC?pair={pair}&interval=1"
        try:
            data = await self._rest_get(url)
            result = data.get("result", {})
            ohlc = result.get(mapped, [])
            candles = []
            for row in ohlc[-limit:]:
                candles.append(Candle(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(row[0], tz=timezone.utc),
                    open=Decimal(str(row[1])),
                    high=Decimal(str(row[2])),
                    low=Decimal(str(row[3])),
                    close=Decimal(str(row[4])),
                    volume=Decimal(str(row[6])),
                    asset_class=self.asset_class,
                ))
            return candles
        except Exception as exc:
            logger.error("Kraken OHLC error: %s", exc)
            return []

    async def stream_prices(self, callback: Callable[[Price], None]) -> None:
        import websockets
        uri = "wss://ws.kraken.com/"
        subscribe = {
            "event": "subscribe",
            "pair": self.symbols,
            "subscription": {"name": "ticker"},
        }
        try:
            async with websockets.connect(uri, ping_interval=20) as ws:
                await ws.send(json.dumps(subscribe))
                async for message in ws:
                    data = json.loads(message)
                    if isinstance(data, dict) and data.get("event") == "heartbeat":
                        continue
                    if isinstance(data, list) and len(data) >= 2:
                        ticker = data[1]
                        pair = self.unmap_symbol(data[-1])
                        price = Decimal(str(ticker.get("c", [0])[0]))
                        bid = Decimal(str(ticker.get("b", [0])[0]))
                        ask = Decimal(str(ticker.get("a", [0])[0]))
                        callback(Price(
                            symbol=pair,
                            value=price,
                            timestamp=datetime.now(timezone.utc),
                            bid=bid,
                            ask=ask,
                            asset_class=self.asset_class,
                        ))
        except Exception as exc:
            logger.error("Kraken WebSocket error: %s", exc)

    async def get_order_book(self, symbol: str, depth: int = 10) -> Optional[OrderBook]:
        mapped = self.map_symbol(symbol)
        pair = urllib.parse.quote(mapped)
        url = f"{self.base_url}/Depth?pair={pair}&count={depth}"
        try:
            data = await self._rest_get(url)
            result = data.get("result", {})
            book = result.get(mapped, {})
            bids = [OrderBookLevel(price=Decimal(str(b[0])), quantity=Decimal(str(b[1])), order_count=int(b[2]) if len(b) > 2 else 0) for b in book.get("bids", [])[:depth]]
            asks = [OrderBookLevel(price=Decimal(str(a[0])), quantity=Decimal(str(a[1])), order_count=int(a[2]) if len(a) > 2 else 0) for a in book.get("asks", [])[:depth]]
            return OrderBook(symbol=symbol, bids=bids, asks=asks, timestamp=datetime.now(timezone.utc), asset_class=self.asset_class)
        except Exception as exc:
            logger.error("Kraken order book error: %s", exc)
            return None

    async def _rest_get(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_get, url)

    def _sync_get(self, url: str) -> dict:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
