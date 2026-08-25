from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

import numpy as np

from src.ai.backtest_engine import BacktestEngine, BacktestResult
from src.data.models import AssetClass, Candle

logger = logging.getLogger(__name__)


@dataclass
class MonteCarloResult:
    expected_return: float
    std_dev: float
    median_return: float
    percentile_5: float
    percentile_95: float
    max_drawdown_avg: float
    success_probability: float
    simulations: int = 1000


class MonteCarloBacktester:
    def __init__(self, backtest_engine: BacktestEngine, simulations: int = 1000) -> None:
        self.backtest_engine = backtest_engine
        self.simulations = simulations

    def run_monte_carlo(self, strategy, candles: list[Candle], asset_class: AssetClass, initial_capital: Decimal = Decimal("100000")) -> MonteCarloResult:
        if len(candles) < 2:
            return MonteCarloResult(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        returns = []
        for i in range(1, len(candles)):
            if candles[i-1].close > 0:
                ret = float((candles[i].close - candles[i-1].close) / candles[i-1].close)
                returns.append(ret)

        if not returns:
            return MonteCarloResult(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        mu = np.mean(returns)
        sigma = np.std(returns)
        final_values = []
        max_drawdowns = []

        for _ in range(self.simulations):
            sim_returns = np.random.normal(mu, sigma, len(returns))
            equity = [float(initial_capital)]
            for ret in sim_returns:
                equity.append(equity[-1] * (1.0 + ret))
            final_values.append(equity[-1])
            peak = np.maximum.accumulate(equity)
            drawdowns = (peak - equity) / (peak + 1e-9)
            max_drawdowns.append(float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0)

        final_values = np.array(final_values)
        max_drawdowns = np.array(max_drawdowns)
        total_returns = (final_values - float(initial_capital)) / float(initial_capital)

        success_prob = float(np.mean(total_returns > 0))

        return MonteCarloResult(
            expected_return=float(np.mean(total_returns)),
            std_dev=float(np.std(total_returns)),
            median_return=float(np.median(total_returns)),
            percentile_5=float(np.percentile(total_returns, 5)),
            percentile_95=float(np.percentile(total_returns, 95)),
            max_drawdown_avg=float(np.mean(max_drawdowns)),
            success_probability=success_prob,
            simulations=self.simulations,
        )
