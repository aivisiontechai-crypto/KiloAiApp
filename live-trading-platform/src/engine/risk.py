from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

import numpy as np

from src.data.models import AssetClass, Trade
from src.portfolio.ledger import AssetLedger

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
    concentration: float = 0.0
    max_position_size: float = 0.0
    sharpe: float = 0.0
    sortino: float = 0.0
    metadata: dict = field(default_factory=dict)


class RiskAnalyzer:
    def __init__(self, confidence_level: float = 0.95) -> None:
        self.confidence_level = confidence_level
        self._max_concentration = 0.3
        self._max_position_size = 0.1

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

    def calculate_correlation_matrix(self, symbols: list[str], price_history: dict[str, list[float]]) -> dict:
        if len(symbols) < 2:
            return {}
        returns = {}
        for symbol in symbols:
            prices = price_history.get(symbol, [])
            if len(prices) > 1:
                ret = np.diff(prices) / np.array(prices[:-1])
                returns[symbol] = ret
        matrix = {}
        for s1 in symbols:
            for s2 in symbols:
                if s1 in returns and s2 in returns:
                    min_len = min(len(returns[s1]), len(returns[s2]))
                    if min_len > 0:
                        corr = float(np.corrcoef(returns[s1][:min_len], returns[s2][:min_len])[0][1])
                        matrix[f"{s1}_{s2}"] = corr
        return matrix

    def calculate_concentration(self, positions: list[dict], total_value: float) -> float:
        if total_value <= 0 or not positions:
            return 0.0
        max_pos_value = max((float(p.get("market_value", 0) or 0) for p in positions), default=0)
        return max_pos_value / total_value if total_value > 0 else 0.0

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

    def calculate_sharpe(self, returns: list[float], risk_free_rate: float = 0.05) -> float:
        if not returns:
            return 0.0
        excess = np.array(returns) - risk_free_rate / 252
        return float(np.mean(excess) / (np.std(excess) + 1e-9))

    def calculate_sortino(self, returns: list[float], risk_free_rate: float = 0.05) -> float:
        if not returns:
            return 0.0
        excess = np.array(returns) - risk_free_rate / 252
        downside = excess[excess < 0]
        if len(downside) == 0:
            return 0.0
        return float(np.mean(excess) / (np.std(downside) + 1e-9))

    def check_limits(self, positions: list[dict], total_value: float) -> dict:
        concentration = self.calculate_concentration(positions, total_value)
        violations = []
        if concentration > self._max_concentration:
            violations.append(f"Concentration limit exceeded: {concentration:.2%} > {self._max_concentration:.2%}")
        for pos in positions:
            weight = float(pos.get("market_value", 0) or 0) / total_value if total_value > 0 else 0
            if weight > self._max_position_size:
                violations.append(f"Position size limit exceeded: {pos.get('symbol')} at {weight:.2%}")
        return {
            "concentration": concentration,
            "violations": violations,
            "passed": len(violations) == 0,
        }

    def analyze_portfolio(self, trades: list[dict], current_prices: dict[str, float]) -> RiskMetrics:
        returns = []
        for i in range(1, len(trades)):
            if trades[i]["side"] == "sell" and trades[i-1]["side"] == "buy":
                ret = (trades[i]["price"] - trades[i-1]["price"]) / trades[i-1]["price"]
                returns.append(ret)
        var_95 = self.calculate_var(returns, 0.95)
        var_99 = self.calculate_var(returns, 0.99)
        market_returns = [0.01, -0.005, 0.02, -0.01, 0.005]
        asset_returns = returns[:len(market_returns)] if len(returns) >= len(market_returns) else returns + [0.0] * (len(market_returns) - len(returns))
        beta = self.calculate_beta(asset_returns, market_returns)
        correlation = self.calculate_correlation(asset_returns, market_returns)
        sharpe = self.calculate_sharpe(returns)
        sortino = self.calculate_sortino(returns)
        symbols = list(current_prices.keys())
        positions = [{"symbol": s, "quantity": 1.0, "average_entry_price": current_prices[s], "market_value": current_prices[s]} for s in symbols]
        total_value = sum(current_prices.values())
        shocks = {s: -0.2 for s in symbols}
        stress_loss = self.stress_test(positions, shocks)
        concentration = self.calculate_concentration(positions, total_value)
        return RiskMetrics(
            symbol=", ".join(symbols),
            var_95=var_95,
            var_99=var_99,
            stress_test_loss=stress_loss,
            beta=beta,
            correlation=correlation,
            concentration=concentration,
            sharpe=sharpe,
            sortino=sortino,
            metadata={"returns": returns},
        )
