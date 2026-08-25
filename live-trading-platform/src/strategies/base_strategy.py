from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Side, StrategySignal

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    def __init__(self, name: str, asset_class: AssetClass, symbols: list[str], parameters: dict) -> None:
        self.name = name
        self.asset_class = asset_class
        self.symbols = symbols
        self.parameters = parameters
        self._last_signal_time: dict[str, datetime] = {}

    @abstractmethod
    def on_candle(self, candle) -> Optional[StrategySignal]:
        raise NotImplementedError

    def _cooldown_ok(self, symbol: str, cooldown_seconds: int = 60) -> bool:
        last = self._last_signal_time.get(symbol)
        if last is None:
            return True
        return (datetime.utcnow() - last).total_seconds() >= cooldown_seconds

    def _record_signal(self, symbol: str) -> None:
        self._last_signal_time[symbol] = datetime.utcnow()
