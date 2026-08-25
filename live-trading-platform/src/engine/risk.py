from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import numpy as np

from src.data.models import AssetClass, Trade

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    symbol: str
    var_95: float = 0.0
    var_99: float = 0.0
    margin_requirement: float = 0.0
    leverage: float = 1.0
    stress_test_loss: float = 0.0
    beta: float = 1.0
    correlation: float = 0.0
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RiskAnalyzer:
    def __init__(self, confidence_level: float = 0.95) -> None:
        self.confidence_level = confidence_level

    def calculate_var(self, returns: list[float], confidence: float = 0.95) -> float:
        if not returns:
            return 0.0
        returns_array = np.array(returns)
        return float(np.percentile(returns_array, (1 - confidence) * 100))

    def calculate_beta(self, asset_returns: list[float], market_returns: list[float]) -> float:
        if not asset_returns or not market_returns or len(asset_returns) != len(market_returns):
            return 1.0
        covariance = np.cov(asset_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        if market_variance == 0:
            return 1.0
        return float(covariance / market_variance)

    def calculate_correlation(self, asset_returns: list[float], market_returns: list[float]) -> float:
        if not asset_returns or not market_returns or len(asset_returns) != len(market_returns):
            return 0.0
        correlation_matrix = np.corrcoef(asset_returns, market_returns)
        return float(correlation_matrix[0][1])

    def stress_test(self, positions: list[dict], shocks: dict[str, float]) -> float:
        total_loss = 0.0
        for pos in positions:
            symbol = pos.get("symbol", "")
            quantity = float(pos.get("quantity", 0))
            avg_price = float(pos.get("average_entry_price", 0))
            shock = shocks.get(symbol, 0.0)
            loss = quantity * avg_price * abs(shock)
            total_loss += loss
        return total_loss

    def calculate_margin_requirement(self, position_value: float, leverage: float = 1.0) -> float:
        return position_value / leverage

    def analyze_portfolio(self, trades: list[dict], current_prices: dict[str, float]) -> RiskMetrics:
        returns = []
        for i in range(1, len(trades)):
            if trades[i]["side"] == "sell" and trades[i-1]["side"] == "buy":
                ret = (trades[i]["price"] - trades[i-1]["price"]) / trades[i-1]["price"]
                returns.append(ret)
        var_95 = self.calculate_var(returns, 0.95)
        var_99 = self.calculate_var(returns, 0.99)
        symbols = list(current_prices.keys())
        market_returns = [0.01, -0.005, 0.02, -0.01, 0.005]
        asset_returns = returns[:len(market_returns)] if len(returns) >= len(market_returns) else returns + [0.0] * (len(market_returns) - len(returns))
        beta = self.calculate_beta(asset_returns, market_returns)
        correlation = self.calculate_correlation(asset_returns, market_returns)
        positions = [{"symbol": s, "quantity": 1.0, "average_entry_price": current_prices[s]} for s in symbols]
        shocks = {s: -0.2 for s in symbols}
        stress_loss = self.stress_test(positions, shocks)
        return RiskMetrics(
            symbol=", ".join(symbols),
            var_95=var_95,
            var_99=var_99,
            stress_test_loss=stress_loss,
            beta=beta,
            correlation=correlation,
        )
