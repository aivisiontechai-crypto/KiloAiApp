from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DrawingTool:
    id: str
    tool_type: str
    symbol: str
    points: list[dict]
    color: str = "#00d4ff"
    metadata: dict = field(default_factory=dict)


class DrawingTools:
    @staticmethod
    def trendline(points: list[dict], color: str = "#00d4ff") -> DrawingTool:
        return DrawingTool(
            id=str(id(points)),
            tool_type="trendline",
            symbol=points[0].get("symbol", "") if points else "",
            points=points,
            color=color,
        )

    @staticmethod
    def fibonacci_retracement(high: dict, low: dict, color: str = "#00d4ff") -> DrawingTool:
        points = [high, low]
        levels = {}
        if high.get("price") and low.get("price"):
            diff = Decimal(str(high["price"])) - Decimal(str(low["price"]))
            for pct in [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]:
                levels[str(pct)] = float(Decimal(str(high["price"])) - diff * Decimal(str(pct)))
        return DrawingTool(
            id=str(id(points)),
            tool_type="fibonacci",
            symbol=high.get("symbol", ""),
            points=points,
            color=color,
            metadata={"levels": levels},
        )

    @staticmethod
    def horizontal_line(price: Decimal, symbol: str, color: str = "#00d4ff") -> DrawingTool:
        return DrawingTool(
            id=str(id((str(price), symbol))),
            tool_type="horizontal",
            symbol=symbol,
            points=[{"price": float(price)}],
            color=color,
        )
