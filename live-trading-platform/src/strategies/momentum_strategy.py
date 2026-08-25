from __future__ import annotations

import logging
from collections import deque
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Side, StrategySignal
from src.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class MomentumStrategy(BaseStrategy):
    def __init__(self, name: str, asset_class: AssetClass, symbols: list[str], parameters: dict) -> None:
        super().__init__(name, asset_class, symbols, parameters)
        self.roc_period = int(parameters.get("roc_period", 14))
        self.threshold = Decimal(str(parameters.get("threshold", 0.02)))
        self._prices: dict[str, deque] = {s: deque(maxlen=self.roc_period + 1) for s in symbols}

    def on_candle(self, candle) -> Optional[StrategySignal]:
        for symbol in self.symbols:
            prices = self._prices[symbol]
            if len(prices) <= self.roc_period:
                continue
            prev = prices[-self.roc_period]
            curr = prices[-1]
            if prev == 0:
                continue
            roc = (curr - prev) / prev
            if roc > self.threshold:
                self._record_signal(symbol)
                return StrategySignal(symbol=symbol, side=Side.BUY, confidence=float(min(roc, 1.0)), strategy=self.name)
            if roc < -self.threshold:
                self._record_signal(symbol)
                return StrategySignal(symbol=symbol, side=Side.SELL, confidence=float(min(abs(roc), 1.0)), strategy=self.name)
        return None
