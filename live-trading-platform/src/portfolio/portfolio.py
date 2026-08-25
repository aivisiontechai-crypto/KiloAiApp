from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Trade
from src.portfolio.ledger import AssetLedger, Position

logger = logging.getLogger(__name__)


@dataclass
class MarginAccount:
    asset_class: AssetClass
    cash: Decimal
    buying_power: Decimal
    margin_used: Decimal
    margin_requirement: float
    maintenance_margin: float
    leverage: float = 1.0
    margin_call: bool = False


class Portfolio:
    def __init__(self, initial_capital: dict[AssetClass, tuple[Decimal, str]]) -> None:
        self._ledgers: dict[AssetClass, AssetLedger] = {}
        self._margin_accounts: dict[AssetClass, MarginAccount] = {}
        for ac, (cash, currency) in initial_capital.items():
            self._ledgers[ac] = AssetLedger(ac, cash, currency)
            self._margin_accounts[ac] = MarginAccount(
                asset_class=ac,
                cash=cash,
                buying_power=cash,
                margin_used=Decimal("0"),
                margin_requirement=0.25,
                maintenance_margin=0.25,
            )

    def get_ledger(self, asset_class: AssetClass) -> AssetLedger:
        if asset_class not in self._ledgers:
            self._ledgers[asset_class] = AssetLedger(asset_class, Decimal("0"), "USD")
            self._margin_accounts[asset_class] = MarginAccount(
                asset_class=asset_class,
                cash=Decimal("0"),
                buying_power=Decimal("0"),
                margin_used=Decimal("0"),
                margin_requirement=0.25,
                maintenance_margin=0.25,
            )
        return self._ledgers[asset_class]

    def record_trade(self, trade) -> None:
        ledger = self.get_ledger(trade.asset_class)
        ledger.record_trade(trade)
        self._update_margin(trade.asset_class)

    def _update_margin(self, asset_class: AssetClass) -> None:
        ledger = self._ledgers.get(asset_class)
        margin = self._margin_accounts.get(asset_class)
        if not ledger or not margin:
            return
        total_value = ledger.get_total_value()
        margin.margin_used = ledger.get_margin_requirement()
        margin.buying_power = total_value * (Decimal("1") / Decimal(str(margin.margin_requirement)))
        margin.leverage = float(total_value / (margin.margin_used + Decimal("0.0001")))
        margin.margin_call = margin.leverage > 4.0

    def get_positions(self) -> dict[AssetClass, list[dict]]:
        result = {}
        for ac, ledger in self._ledgers.items():
            result[ac] = ledger.get_positions()
        return result

    def get_trades(self) -> dict[AssetClass, list[dict]]:
        result = {}
        for ac, ledger in self._ledgers.items():
            result[ac] = ledger.get_trades()
        return result

    def get_total_value(self, current_prices: Optional[dict[AssetClass, dict[str, Decimal]]] = None) -> Decimal:
        total = Decimal("0")
        for ac, ledger in self._ledgers.items():
            prices = current_prices.get(ac) if current_prices else None
            total += ledger.get_total_value(prices)
        return total

    def get_cash(self) -> dict[AssetClass, Decimal]:
        return {ac: ledger.cash for ac, ledger in self._ledgers.items()}

    def get_margin_accounts(self) -> dict[AssetClass, dict]:
        result = {}
        for ac, margin in self._margin_accounts.items():
            result[ac] = {
                "asset_class": ac.value,
                "cash": float(margin.cash),
                "buying_power": float(margin.buying_power),
                "margin_used": float(margin.margin_used),
                "margin_requirement": margin.margin_requirement,
                "maintenance_margin": margin.maintenance_margin,
                "leverage": margin.leverage,
                "margin_call": margin.margin_call,
            }
        return result

    def get_pnl_report(self, period: str = "all") -> dict:
        all_trades = []
        for ledger in self._ledgers.values():
            all_trades.extend(ledger._trades)
        if period == "today":
            today = datetime.utcnow().date()
            all_trades = [t for t in all_trades if t.timestamp.date() == today]
        realized = sum((t.price - self._ledgers[t.asset_class]._positions.get(t.symbol, Position(t.symbol, Decimal("0"), Decimal("0"))).average_entry_price) * t.quantity for t in all_trades if t.side.value == "sell")
        return {
            "realized_pnl": float(realized),
            "trade_count": len(all_trades),
            "period": period,
        }
