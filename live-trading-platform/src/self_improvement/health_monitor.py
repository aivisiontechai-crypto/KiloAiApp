from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    consecutive_losses: int = 0
    max_drawdown: float = 0.0
    win_rate: float = 1.0
    auto_rollback_count: int = 0
    last_check: datetime = field(default_factory=datetime.utcnow)


class StrategyHealthMonitor:
    def __init__(self, max_consecutive_losses: int = 5, max_drawdown_threshold: float = 0.2) -> None:
        self.max_consecutive_losses = max_consecutive_losses
        self.max_drawdown_threshold = max_drawdown_threshold
        self._strategies: dict[str, HealthMetrics] = {}

    def register_strategy(self, name: str, initial_equity: float = 100000.0) -> None:
        self._strategies[name] = HealthMetrics()

    def record_trade(self, name: str, pnl: Decimal, current_equity: float) -> None:
        if name not in self._strategies:
            self.register_strategy(name)
        metrics = self._strategies[name]
        if pnl < 0:
            metrics.consecutive_losses += 1
        else:
            metrics.consecutive_losses = 0
        metrics.last_check = datetime.utcnow()

    def _is_healthy(self, name: str) -> bool:
        metrics = self._strategies.get(name)
        if not metrics:
            return True
        if metrics.consecutive_losses >= self.max_consecutive_losses:
            return False
        if metrics.max_drawdown >= self.max_drawdown_threshold:
            return False
        if metrics.win_rate < 0.2:
            return False
        return True

    def reset(self, name: str, initial_equity: float) -> None:
        if name in self._strategies:
            self._strategies[name] = HealthMetrics()

    def get_metrics(self, name: str) -> Optional[HealthMetrics]:
        return self._strategies.get(name)
