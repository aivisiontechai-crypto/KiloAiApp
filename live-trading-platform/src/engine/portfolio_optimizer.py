from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PortfolioOptimizationResult:
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    method: str


class PortfolioOptimizer:
    def __init__(self, risk_free_rate: float = 0.05):
        self.risk_free_rate = risk_free_rate

    def optimize(self, returns: dict[str, list[float]], covariances: dict[tuple[str, str], float], method: str = "sharpe") -> PortfolioOptimizationResult:
        symbols = list(returns.keys())
        if len(symbols) < 2:
            weights = {s: 1.0 / len(symbols) for s in symbols}
            avg_returns = {s: sum(r) / len(r) if r else 0.0 for s, r in returns.items()}
            expected = sum(weights[s] * avg_returns[s] for s in symbols)
            variance = sum(weights.get(s1, 0) * weights.get(s2, 0) * covariances.get((s1, s2), 0.0) for s1 in symbols for s2 in symbols)
            return PortfolioOptimizationResult(weights=weights, expected_return=expected, volatility=variance ** 0.5, sharpe_ratio=(expected - self.risk_free_rate) / (variance ** 0.5 + 1e-9), method=method)
        best = None
        best_score = float("-inf")
        steps = 21
        for w1 in [i / (steps - 1) for i in range(steps)]:
            w2 = 1.0 - w1
            weights = {symbols[0]: w1, symbols[1]: w2}
            avg_returns = {s: sum(r) / len(r) if r else 0.0 for s, r in returns.items()}
            expected = sum(weights[s] * avg_returns[s] for s in symbols)
            variance = sum(weights.get(s1, 0) * weights.get(s2, 0) * covariances.get((s1, s2), 0.0) for s1 in symbols for s2 in symbols)
            volatility = variance ** 0.5
            sharpe = (expected - self.risk_free_rate) / (volatility + 1e-9)
            if method == "sharpe" and sharpe > best_score:
                best_score = sharpe
                best = (weights, expected, volatility, sharpe)
            elif method == "min_variance" and volatility < best_score:
                best_score = volatility
                best = (weights, expected, volatility, sharpe)
        if best is None:
            weights = {s: 1.0 / len(symbols) for s in symbols}
            avg_returns = {s: sum(r) / len(r) if r else 0.0 for s, r in returns.items()}
            expected = sum(weights[s] * avg_returns[s] for s in symbols)
            variance = sum(weights.get(s1, 0) * weights.get(s2, 0) * covariances.get((s1, s2), 0.0) for s1 in symbols for s2 in symbols)
            volatility = variance ** 0.5
            sharpe = (expected - self.risk_free_rate) / (volatility + 1e-9)
            best = (weights, expected, volatility, sharpe)
        weights, expected, volatility, sharpe = best
        return PortfolioOptimizationResult(weights=weights, expected_return=expected, volatility=volatility, sharpe_ratio=sharpe, method=method)
