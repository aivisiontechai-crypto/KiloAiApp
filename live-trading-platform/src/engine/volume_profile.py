from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VolumeProfileLevel:
    price: Decimal
    volume: Decimal
    tick_count: int = 0


class VolumeProfile:
    def __init__(self, symbol: str, buckets: int = 20):
        self.symbol = symbol
        self.buckets = buckets
        self._levels: list[VolumeProfileLevel] = []
        self._total_volume = Decimal("0")

    def add_candle(self, high: Decimal, low: Decimal, volume: Decimal) -> None:
        if not self._levels:
            min_p = low
            max_p = high
        else:
            prices = [Decimal(str(l.price)) for l in self._levels]
            min_p = min(min_p, low, *prices)
            max_p = max(max_p, high, *prices)
        bucket_size = (max_p - min_p) / Decimal(str(self.buckets)) if max_p > min_p else Decimal("1")
        if bucket_size <= 0:
            bucket_size = Decimal("1")
        new_levels = [VolumeProfileLevel(price=min_p + bucket_size * i, volume=Decimal("0")) for i in range(self.buckets)]
        for level in self._levels:
            bucket_idx = int((level.price - min_p) / bucket_size)
            if 0 <= bucket_idx < self.buckets:
                new_levels[bucket_idx].volume += level.volume
                new_levels[bucket_idx].tick_count += level.tick_count
        for i in range(self.buckets):
            p = min_p + bucket_size * i
            if low <= p <= high:
                new_levels[i].volume += volume
                new_levels[i].tick_count += 1
        self._levels = new_levels
        self._total_volume += volume

    def get_profile(self) -> list[dict]:
        if not self._levels:
            return []
        max_vol = max((l.volume for l in self._levels), default=Decimal("1"))
        if max_vol <= 0:
            max_vol = Decimal("1")
        result = []
        for level in self._levels:
            result.append({
                "price": float(level.price),
                "volume": float(level.volume),
                "tick_count": level.tick_count,
                "relative_volume": float(level.volume / max_vol),
            })
        result.sort(key=lambda x: x["price"])
        return result

    def get_poc(self) -> Optional[float]:
        if not self._levels:
            return None
        poc = max(self._levels, key=lambda l: l.volume)
        return float(poc.price)

    def get_value_area(self, percent: float = 0.7) -> dict:
        profile = sorted(self._levels, key=lambda l: l.volume, reverse=True)
        if not profile:
            return {"poc": None, "vah": None, "val": None}
        total = self._total_volume
        target = total * Decimal(str(percent))
        included = []
        cum_vol = Decimal("0")
        for level in profile:
            included.append(level)
            cum_vol += level.volume
            if cum_vol >= target:
                break
        prices = [Decimal(str(l.price)) for l in included]
        return {
            "poc": float(max(profile, key=lambda l: l.volume).price),
            "vah": float(max(prices)) if prices else None,
            "val": float(min(prices)) if prices else None,
        }
