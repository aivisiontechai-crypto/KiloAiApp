from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Callable, Optional

from src.data.models import AssetClass, Candle, Price

logger = logging.getLogger(__name__)


class BaseDataAdapter:
    asset_class: AssetClass = AssetClass.CRYPTO

    async def connect(self) -> None:
        raise NotImplementedError

    async def disconnect(self) -> None:
        raise NotImplementedError

    async def get_historical_candles(self, symbol: str, limit: int = 100) -> list[Candle]:
        raise NotImplementedError

    async def stream_prices(self, callback: Callable[[Price], None]) -> None:
        raise NotImplementedError

    def map_symbol(self, symbol: str) -> str:
        return symbol

    def unmap_symbol(self, symbol: str) -> str:
        return symbol


class DataManager:
    def __init__(self) -> None:
        self._adapters: dict[AssetClass, BaseDataAdapter] = {}
        self._running = False
        self._lock = asyncio.Lock()

    def register_adapter(self, adapter: BaseDataAdapter) -> None:
        self._adapters[adapter.asset_class] = adapter

    def get_adapter(self, asset_class: AssetClass) -> Optional[BaseDataAdapter]:
        return self._adapters.get(asset_class)

    def get_adapters_by_asset_class(self) -> dict[AssetClass, BaseDataAdapter]:
        return dict(self._adapters)

    async def start(self) -> None:
        async with self._lock:
            self._running = True
            for adapter in self._adapters.values():
                try:
                    await adapter.connect()
                except Exception as exc:
                    logger.error("Adapter connect error: %s", exc)

    async def stop(self) -> None:
        async with self._lock:
            self._running = False
            for adapter in self._adapters.values():
                try:
                    await adapter.disconnect()
                except Exception as exc:
                    logger.error("Adapter disconnect error: %s", exc)

    @property
    def is_running(self) -> bool:
        return self._running
