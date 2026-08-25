from __future__ import annotations

import copy
import itertools
import logging
import random
from dataclasses import dataclass, field
from typing import Any

from src.ai.backtest_engine import BacktestEngine, BacktestResult
from src.ai.strategy_researcher import StrategyCandidate
from src.data.models import AssetClass, Candle
from src.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    best_parameters: dict
    best_score: float
    all_results: list[dict] = field(default_factory=list)


class AIOptimizer:
    def __init__(self, backtest_engine: BacktestEngine, method: str = "grid_search") -> None:
        self.backtest_engine = backtest_engine
        self.method = method

    def optimize(self, strategy_class, candles: list[Candle], asset_class: AssetClass, param_grid: dict) -> OptimizationResult:
        candidates = []
        if self.method == "grid_search":
            keys = list(param_grid.keys())
            for values in itertools.product(*param_grid.values()):
                params = dict(zip(keys, values))
                strategy = strategy_class(name="opt", asset_class=asset_class, symbols=[candles[0].symbol] if candles else [], parameters=params)
                result = self.backtest_engine.run_backtest(strategy, candles, asset_class)
                candidates.append({"params": params, "score": result.sharpe_ratio, "result": result})
        elif self.method == "random_search":
            for _ in range(20):
                params = {k: random.choice(v) for k, v in param_grid.items()}
                strategy = strategy_class(name="opt", asset_class=asset_class, symbols=[candles[0].symbol] if candles else [], parameters=params)
                result = self.backtest_engine.run_backtest(strategy, candles, asset_class)
                candidates.append({"params": params, "score": result.sharpe_ratio, "result": result})
        best = max(candidates, key=lambda x: x["score"])
        return OptimizationResult(
            best_parameters=best["params"],
            best_score=best["score"],
            all_results=candidates,
        )
