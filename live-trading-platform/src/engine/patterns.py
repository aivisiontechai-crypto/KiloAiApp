from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    id: str
    pattern_type: str
    symbol: str
    start_index: int
    end_index: int
    confidence: float
    price_target: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PatternRecognition:
    @staticmethod
    def detect_head_and_shoulders(prices: list[float], volumes: list[float]) -> Optional[Pattern]:
        if len(prices) < 30:
            return None
        left_peak = max(prices[5:15])
        left_idx = prices[5:15].index(left_peak) + 5
        head = max(prices[10:25])
        head_idx = prices[10:25].index(head) + 10
        right_peak = max(prices[20:30])
        right_idx = prices[20:30].index(right_peak) + 20
        if head > left_peak and head > right_peak and abs(left_peak - right_peak) / max(left_peak, right_peak) < 0.05:
            neckline = min(prices[left_idx:head_idx] + prices[head_idx:right_idx])
            confidence = 0.7 if head - neckline > 0 else 0.3
            return Pattern(
                id="hs_" + str(id(prices)),
                pattern_type="head_and_shoulders",
                symbol="",
                start_index=left_idx,
                end_index=right_idx,
                confidence=confidence,
                price_target=Decimal(str(neckline - (head - neckline))),
                stop_loss=Decimal(str(head)),
                metadata={"head_idx": head_idx, "neckline": float(neckline)},
            )
        return None

    @staticmethod
    def detect_double_top(prices: list[float], volumes: list[float]) -> Optional[Pattern]:
        if len(prices) < 20:
            return None
        first_top = max(prices[5:12])
        first_idx = prices[5:12].index(first_top) + 5
        second_top = max(prices[12:20])
        second_idx = prices[12:20].index(second_top) + 12
        valley = min(prices[first_idx:second_idx]) if second_idx > first_idx else prices[first_idx]
        if first_top > 0 and second_top > 0 and abs(first_top - second_top) / max(first_top, second_top) < 0.03 and valley < min(first_top, second_top) * 0.97:
            confidence = 0.65
            return Pattern(
                id="dt_" + str(id(prices)),
                pattern_type="double_top",
                symbol="",
                start_index=first_idx,
                end_index=second_idx,
                confidence=confidence,
                price_target=Decimal(str(valley - (min(first_top, second_top) - valley))),
                stop_loss=Decimal(str(max(first_top, second_top) * 1.01)),
                metadata={"first_idx": first_idx, "second_idx": second_idx},
            )
        return None

    @staticmethod
    def detect_double_bottom(prices: list[float], volumes: list[float]) -> Optional[Pattern]:
        if len(prices) < 20:
            return None
        first_bottom = min(prices[5:12])
        first_idx = prices[5:12].index(first_bottom) + 5
        second_bottom = min(prices[12:20])
        second_idx = prices[12:20].index(second_bottom) + 12
        peak = max(prices[first_idx:second_idx]) if second_idx > first_idx else prices[first_idx]
        if first_bottom > 0 and second_bottom > 0 and abs(first_bottom - second_bottom) / min(first_bottom, second_bottom) < 0.03 and peak > max(first_bottom, second_bottom) * 1.03:
            confidence = 0.65
            return Pattern(
                id="db_" + str(id(prices)),
                pattern_type="double_bottom",
                symbol="",
                start_index=first_idx,
                end_index=second_idx,
                confidence=confidence,
                price_target=Decimal(str(peak + (peak - min(first_bottom, second_bottom)))),
                stop_loss=Decimal(str(min(first_bottom, second_bottom) * 0.99)),
                metadata={"first_idx": first_idx, "second_idx": second_idx},
            )
        return None

    @staticmethod
    def detect_triangle(prices: list[float], volumes: list[float]) -> Optional[Pattern]:
        if len(prices) < 20:
            return None
        highs = [max(prices[i:i+5]) for i in range(0, len(prices)-4, 5)]
        lows = [min(prices[i:i+5]) for i in range(0, len(prices)-4, 5)]
        if len(highs) < 3 or len(lows) < 3:
            return None
        high_slope = (highs[-1] - highs[0]) / (len(highs) - 1)
        low_slope = (lows[-1] - lows[0]) / (len(lows) - 1)
        if abs(high_slope) < 0.001 and low_slope > 0.001:
            ptype = "ascending_triangle"
            confidence = 0.6
        elif high_slope < -0.001 and abs(low_slope) < 0.001:
            ptype = "descending_triangle"
            confidence = 0.6
        elif high_slope < -0.001 and low_slope > 0.001:
            ptype = "symmetrical_triangle"
            confidence = 0.55
        else:
            return None
        return Pattern(
            id="tri_" + str(id(prices)),
            pattern_type=ptype,
            symbol="",
            start_index=0,
            end_index=len(prices) - 1,
            confidence=confidence,
            metadata={"high_slope": high_slope, "low_slope": low_slope},
        )

    @staticmethod
    def scan_all(prices: list[float], volumes: Optional[list[float]] = None) -> list[dict]:
        if volumes is None:
            volumes = [0.0] * len(prices)
        patterns = []
        for detector in [PatternRecognition.detect_head_and_shoulders, PatternRecognition.detect_double_top, PatternRecognition.detect_double_bottom, PatternRecognition.detect_triangle]:
            try:
                result = detector(prices, volumes)
                if result:
                    patterns.append({
                        "pattern_type": result.pattern_type,
                        "confidence": result.confidence,
                        "start_index": result.start_index,
                        "end_index": result.end_index,
                        "price_target": float(result.price_target) if result.price_target else None,
                        "stop_loss": float(result.stop_loss) if result.stop_loss else None,
                        "metadata": result.metadata,
                    })
            except Exception as exc:
                logger.debug("Pattern detection error: %s", exc)
        return patterns
