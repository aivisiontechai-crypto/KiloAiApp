from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.ai.backtest_engine import BacktestEngine, BacktestResult
from src.ai.monte_carlo import MonteCarloBacktester
from src.data.models import AssetClass, Candle
from src.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


@dataclass
class WalkForwardWindow:
    start_date: datetime
    end_date: datetime
    train_candles: list[Candle]
    test_candles: list[Candle]
    best_params: dict = None
    test_result: BacktestResult = None


@dataclass
class WalkForwardResult:
    windows: list[WalkForwardWindow]
    avg_sharpe: float
    avg_return: float
    total_return: float
    max_drawdown: float
    robustness_score: float


class WalkForwardOptimizer:
    def __init__(self, backtest_engine: BacktestEngine, window_size: int = 100, step_size: int = 20) -> None:
        self.backtest_engine = backtest_engine
        self.window_size = window_size
        self.step_size = step_size

    def optimize(self, strategy_class, candles: list[Candle], asset_class: AssetClass, param_grid: dict) -> WalkForwardResult:
        windows = []
        all_returns = []
        all_drawdowns = []

        for i in range(0, len(candles) - self.window_size, self.step_size):
            train = candles[i:i + self.window_size]
            test = candles[i + self.window_size:i + self.window_size + self.step_size]
            if not test:
                continue
            best_params = self._grid_search_best_params(strategy_class, train, asset_class, param_grid)
            strategy = strategy_class(
                name="wf",
                asset_class=asset_class,
                symbols=[candles[0].symbol] if candles else [],
                parameters=best_params,
            )
            test_result = self.backtest_engine.run_backtest(strategy, test, asset_class)
            window = WalkForwardWindow(
                start_date=train[0].timestamp,
                end_date=test[-1].timestamp,
                train_candles=train,
                test_candles=test,
                best_params=best_params,
                test_result=test_result,
            )
            windows.append(window)
            all_returns.append(test_result.total_return)
            all_drawdowns.append(test_result.max_drawdown)

        avg_sharpe = float(np.mean([w.test_result.sharpe_ratio for w in windows])) if windows else 0.0
        avg_return = float(np.mean(all_returns)) if all_returns else 0.0
        total_return = float(np.prod([1.0 + r for r in all_returns]) - 1.0) if all_returns else 0.0
        max_dd = float(np.max(all_drawdowns)) if all_drawdowns else 0.0
        robustness = float(np.mean([1.0 if w.test_result.sharpe_ratio > 0 else 0.0 for w in windows])) if windows else 0.0

        return WalkForwardResult(
            windows=windows,
            avg_sharpe=avg_sharpe,
            avg_return=avg_return,
            total_return=total_return,
            max_drawdown=max_dd,
            robustness_score=robustness,
        )

    def _grid_search_best_params(self, strategy_class, train_candles: list[Candle], asset_class: AssetClass, param_grid: dict) -> dict:
        best_score = -float("inf")
        best_params = {}
        keys = list(param_grid.keys())
        for values in __import__("itertools").product(*param_grid.values()):
            params = dict(zip(keys, values))
            strategy = strategy_class(
                name="opt",
                asset_class=asset_class,
                symbols=[train_candles[0].symbol] if train_candles else [],
                parameters=copy.deepcopy(params),
            )
            result = self.backtest_engine.run_backtest(strategy, train_candles, asset_class)
            if result.sharpe_ratio > best_score:
                best_score = result.sharpe_ratio
                best_params = copy.deepcopy(params)
        return best_params
