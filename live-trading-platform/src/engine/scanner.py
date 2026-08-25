from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Optional

from src.data.models import AssetClass, ScanResult
from src.strategies.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


@dataclass
class ScanCriteria:
    indicator: str
    condition: str
    threshold: Decimal
    asset_class: Optional[AssetClass] = None


class Scanner:
    def __init__(self) -> None:
        self._subscribers: list[Callable[[ScanResult], None]] = []

    def on_scan(self, callback: Callable[[ScanResult], None]) -> None:
        self._subscribers.append(callback)

    def scan_symbol(self, symbol: str, prices: list[Decimal], highs: Optional[list[Decimal]] = None, lows: Optional[list[Decimal]] = None, volumes: Optional[list[Decimal]] = None, criteria: list[ScanCriteria] = None) -> Optional[ScanResult]:
        if not criteria:
            criteria = [
                ScanCriteria(indicator="RSI", condition="below", threshold=Decimal("30")),
                ScanCriteria(indicator="MACD", condition="above", threshold=Decimal("0")),
            ]
        indicator_values = {}
        signals = []
        for c in criteria:
            result = None
            if c.indicator == "RSI":
                result = TechnicalIndicators.rsi(prices)
            elif c.indicator == "MACD":
                result = TechnicalIndicators.macd(prices)
            elif c.indicator == "BollingerBands":
                result = TechnicalIndicators.bollinger_bands(prices)
            elif c.indicator == "Stochastic":
                if highs and lows:
                    result = TechnicalIndicators.stochastic(highs, lows, prices)
            elif c.indicator == "VWAP":
                if highs and lows and volumes:
                    result = TechnicalIndicators.vwap(highs, lows, prices, volumes)
            elif c.indicator == "SuperTrend":
                if highs and lows:
                    result = TechnicalIndicators.supertrend(highs, lows, prices)
            elif c.indicator == "ParabolicSAR":
                if highs and lows:
                    result = TechnicalIndicators.parabolic_sar(highs, lows, prices)
            elif c.indicator == "CCI":
                if highs and lows:
                    result = TechnicalIndicators.cci(highs, lows, prices)
            elif c.indicator == "MFI":
                if highs and lows and volumes:
                    result = TechnicalIndicators.mfi(highs, lows, prices, volumes)
            if result:
                indicator_values[c.indicator] = {
                    "value": float(result.value) if result.value else None,
                    "signal": result.signal,
                }
                if c.condition == "below" and result.value is not None and result.value < c.threshold:
                    signals.append(f"{c.indicator} below {c.threshold}")
                elif c.condition == "above" and result.value is not None and result.value > c.threshold:
                    signals.append(f"{c.indicator} above {c.threshold}")
                elif c.condition == "crosses_above" and result.signal == "bullish":
                    signals.append(f"{c.indicator} bullish cross")
                elif c.condition == "crosses_below" and result.signal == "bearish":
                    signals.append(f"{c.indicator} bearish cross")
        if signals:
            scan = ScanResult(
                symbol=symbol,
                signal=", ".join(signals),
                confidence=min(len(signals) / len(criteria), 1.0),
                indicator_values=indicator_values,
                timestamp=datetime.utcnow(),
                asset_class=AssetClass.CRYPTO,
            )
            for cb in self._subscribers:
                try:
                    cb(scan)
                except Exception as exc:
                    logger.error("Scan callback error: %s", exc)
            return scan
        return None
