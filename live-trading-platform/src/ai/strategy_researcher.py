from __future__ import annotations

import copy
import itertools
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

import numpy as np

from src.data.models import Candle
from src.portfolio.ledger import AssetLedger
from src.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


@dataclass
class StrategyCandidate:
    strategy_class: str
    parameters: dict
    score: float = 0.0
    metrics: dict = field(default_factory=dict)


class AIStrategyResearcher:
    def __init__(self, portfolio) -> None:
        self.portfolio = portfolio

    def generate_candidates(self, strategy_type: str = "ma_crossover", count: int = 10) -> list[StrategyCandidate]:
        candidates = []
        if strategy_type == "ma_crossover":
            fast_periods = range(5, 21, 3)
            slow_periods = range(20, 61, 10)
            for fast, slow in itertools.product(fast_periods, slow_periods):
                if fast < slow:
                    candidates.append(StrategyCandidate(
                        strategy_class="MovingAverageCrossover",
                        parameters={"fast_period": fast, "slow_period": slow},
                    ))
                    if len(candidates) >= count:
                        break
        elif strategy_type == "momentum":
            roc_periods = range(5, 21, 3)
            thresholds = [0.01, 0.02, 0.03, 0.05]
            for roc, thresh in itertools.product(roc_periods, thresholds):
                candidates.append(StrategyCandidate(
                    strategy_class="MomentumStrategy",
                    parameters={"roc_period": roc, "threshold": thresh},
                ))
                if len(candidates) >= count:
                    break
        return candidates[:count]

    def backtest_strategy(self, candidate: StrategyCandidate, candles: list[Candle]) -> StrategyCandidate:
        if len(candles) < 2:
            candidate.score = 0.0
            return candidate
        ledger = AssetLedger(candles[0].asset_class, Decimal("100000"), "USD")
        trades = 0
        pnl = Decimal("0")
        returns = []
        for i in range(1, len(candles)):
            prev_close = candles[i-1].close
            curr_close = candles[i].close
            if prev_close > 0:
                ret = (curr_close - prev_close) / prev_close
                returns.append(float(ret))
            if random.random() > 0.95:
                trades += 1
                pnl += (curr_close - prev_close) * Decimal("0.01")
        candidate.metrics = {"trades": trades, "pnl": float(pnl)}
        if len(returns) > 1:
            candidate.score = float(np.mean(returns) / (np.std(returns) + 1e-9))
        else:
            candidate.score = 0.0
        return candidate

    def evaluate_candidates(self, candidates: list[StrategyCandidate], candles: list[Candle]) -> list[StrategyCandidate]:
        for c in candidates:
            self.backtest_strategy(c, candles)
        return sorted(candidates, key=lambda x: x.score, reverse=True)
