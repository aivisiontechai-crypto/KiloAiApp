from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RiskProfile:
    risk_tolerance: str
    max_position_size: Decimal
    max_portfolio_risk: Decimal
    stop_loss_percent: Decimal
    take_profit_percent: Decimal
    max_open_positions: int
    description: str


class RiskToleranceAssessment:
    @staticmethod
    def assess(answers: dict) -> RiskProfile:
        score = 0
        score += int(answers.get("experience_years", 0)) * 5
        score += int(answers.get("trades_per_month", 0)) * 2
        score += int(answers.get("max_drawdown_tolerance", 0)) * 10
        if answers.get("investment_horizon") == "intraday":
            score += 20
        elif answers.get("investment_horizon") == "swing":
            score += 10
        if answers.get("risk_preference") == "aggressive":
            score += 20
        elif answers.get("risk_preference") == "moderate":
            score += 10
        if score < 20:
            return RiskProfile(
                risk_tolerance="conservative",
                max_position_size=Decimal("0.02"),
                max_portfolio_risk=Decimal("0.01"),
                stop_loss_percent=Decimal("0.01"),
                take_profit_percent=Decimal("0.02"),
                max_open_positions=3,
                description="Low risk tolerance. Focus on capital preservation.",
            )
        elif score < 40:
            return RiskProfile(
                risk_tolerance="moderate",
                max_position_size=Decimal("0.05"),
                max_portfolio_risk=Decimal("0.02"),
                stop_loss_percent=Decimal("0.02"),
                take_profit_percent=Decimal("0.04"),
                max_open_positions=5,
                description="Balanced risk approach. Growth with moderate downside.",
            )
        else:
            return RiskProfile(
                risk_tolerance="aggressive",
                max_position_size=Decimal("0.10"),
                max_portfolio_risk=Decimal("0.05"),
                stop_loss_percent=Decimal("0.03"),
                take_profit_percent=Decimal("0.06"),
                max_open_positions=10,
                description="High risk tolerance. Maximize returns with higher volatility.",
            )


class PositionSizingCalculator:
    @staticmethod
    def calculate_position_size(
        account_balance: Decimal,
        entry_price: Decimal,
        stop_loss_price: Decimal,
        risk_per_trade: Decimal,
        max_position_size: Decimal,
    ) -> Decimal:
        if entry_price <= 0 or stop_loss_price <= 0 or risk_per_trade <= 0:
            return Decimal("0")
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit <= 0:
            return Decimal("0")
        units = (account_balance * risk_per_trade) / risk_per_unit
        max_units = (account_balance * max_position_size) / entry_price
        return min(units, max_units)

    @staticmethod
    def calculate_kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        if avg_loss <= 0:
            return 0.0
        win_loss_ratio = avg_win / avg_loss
        kelly = win_rate - (1 - win_rate) / win_loss_ratio
        return max(0.0, min(kelly, 0.25))
