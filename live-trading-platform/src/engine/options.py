from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OptionGreeks:
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0
    iv: float = 0.0
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OptionContract:
    symbol: str
    underlying: str
    strike: Decimal
    expiry: str
    option_type: str  # "call" or "put"
    quantity: Decimal
    premium: Decimal
    implied_volatility: float = 0.3


class BlackScholes:
    @staticmethod
    def _norm_cdf(x: float) -> float:
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def _norm_pdf(x: float) -> float:
        return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

    @classmethod
    def calculate_greeks(cls, contract: OptionContract, underlying_price: Decimal, risk_free_rate: float = 0.05, days_to_expiry: float = 30) -> OptionGreeks:
        S = float(underlying_price)
        K = float(contract.strike)
        T = days_to_expiry / 365.0
        r = risk_free_rate
        sigma = contract.implied_volatility

        if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
            return OptionGreeks()

        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        if contract.option_type == "call":
            delta = cls._norm_cdf(d1)
            theta = (-(S * cls._norm_pdf(d1) * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * cls._norm_cdf(d2)) / 365.0
            rho = K * T * math.exp(-r * T) * cls._norm_cdf(d2) / 100.0
        else:
            delta = cls._norm_cdf(d1) - 1.0
            theta = (-(S * cls._norm_pdf(d1) * sigma) / (2 * math.sqrt(T)) + r * K * math.exp(-r * T) * cls._norm_cdf(-d2)) / 365.0
            rho = -K * T * math.exp(-r * T) * cls._norm_cdf(-d2) / 100.0

        gamma = cls._norm_pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * cls._norm_pdf(d1) * math.sqrt(T) / 100.0

        return OptionGreeks(
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
            iv=sigma,
            metadata={
                "strike": float(K),
                "expiry_days": days_to_expiry,
                "underlying": float(S),
                "d1": d1,
                "d2": d2,
            }
        )


class OptionsEngine:
    def __init__(self, risk_free_rate: float = 0.05) -> None:
        self.risk_free_rate = risk_free_rate
        self._positions: list[OptionContract] = []

    def add_position(self, contract: OptionContract) -> None:
        self._positions.append(contract)

    def calculate_portfolio_greeks(self, underlying_prices: dict[str, Decimal]) -> dict:
        total_delta = 0.0
        total_gamma = 0.0
        total_theta = 0.0
        total_vega = 0.0
        total_rho = 0.0
        details = []

        for pos in self._positions:
            price = underlying_prices.get(pos.underlying, Decimal("0"))
            days_to_expiry = 30.0
            try:
                from datetime import datetime
                expiry_date = datetime.strptime(pos.expiry, "%Y-%m-%d")
                days_to_expiry = max((expiry_date - datetime.now()).days, 1)
            except Exception:
                pass

            greeks = BlackScholes.calculate_greeks(pos, price, self.risk_free_rate, days_to_expiry)
            total_delta += greeks.delta * float(pos.quantity)
            total_gamma += greeks.gamma * float(pos.quantity)
            total_theta += greeks.theta * float(pos.quantity)
            total_vega += greeks.vega * float(pos.quantity)
            total_rho += greeks.rho * float(pos.quantity)
            details.append({
                "symbol": pos.symbol,
                "type": pos.option_type,
                "strike": float(pos.strike),
                "quantity": float(pos.quantity),
                "delta": greeks.delta,
                "gamma": greeks.gamma,
                "theta": greeks.theta,
                "vega": greeks.vega,
                "rho": greeks.rho,
                "iv": greeks.iv,
            })

        return {
            "total_delta": total_delta,
            "total_gamma": total_gamma,
            "total_theta": total_theta,
            "total_vega": total_vega,
            "total_rho": total_rho,
            "positions": details,
        }
