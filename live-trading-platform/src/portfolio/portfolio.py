from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass
from src.portfolio.ledger import AssetLedger

logger = logging.getLogger(__name__)


class Portfolio:
    def __init__(self, initial_capital: dict[AssetClass, tuple[Decimal, str]]) -> None:
        self._ledgers: dict[AssetClass, AssetLedger] = {}
        for ac, (cash, currency) in initial_capital.items():
            self._ledgers[ac] = AssetLedger(ac, cash, currency)

    def get_ledger(self, asset_class: AssetClass) -> AssetLedger:
        if asset_class not in self._ledgers:
            self._ledgers[asset_class] = AssetLedger(asset_class, Decimal("0"), "USD")
        return self._ledgers[asset_class]

    def record_trade(self, trade) -> None:
        ledger = self.get_ledger(trade.asset_class)
        ledger.record_trade(trade)

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
