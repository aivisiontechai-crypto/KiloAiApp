from __future__ import annotations

import logging
from collections import deque
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Side, StrategySignal
from src.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class MovingAverageCrossover(BaseStrategy):
    def __init__(self, name: str, asset_class: AssetClass, symbols: list[str], parameters: dict) -> None:
        super().__init__(name, asset_class, symbols, parameters)
        self.fast_period = int(parameters.get("fast_period", 10))
        self.slow_period = int(parameters.get("slow_period", 30))
        self._prices: dict[str, deque] = {s: deque(maxlen=self.slow_period + 1) for s in symbols}
        self._prev_rel: dict[str, Optional[bool]] = {s: None for s in symbols}

    def on_candle(self, candle) -> Optional[StrategySignal]:
        for symbol in self.symbols:
            price = self._prices[symbol]
            if len(price) < self.slow_period:
                continue
            fast = sum(list(price)[-self.fast_period:]) / Decimal(self.fast_period)
            slow = sum(list(price)[-self.slow_period:]) / Decimal(self.slow_period)
            rel = fast > slow
            prev = self._prev_rel[symbol]
            if prev is not None and not prev and rel:
                self._record_signal(symbol)
                return StrategySignal(symbol=symbol, side=Side.BUY, confidence=float((fast - slow) / slow), strategy=self.name)
            if prev is not None and prev and not rel:
                self._record_signal(symbol)
                return StrategySignal(symbol=symbol, side=Side.SELL, confidence=float((slow - fast) / slow), strategy=self.name)
            self._prev_rel[symbol] = rel
        return None
