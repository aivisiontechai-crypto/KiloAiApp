from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Trade

logger = logging.getLogger(__name__)


class AssetLedger:
    def __init__(self, asset_class: AssetClass, cash: Decimal, currency: str = "USD") -> None:
        self.asset_class = asset_class
        self.cash = cash
        self.currency = currency
        self._positions: dict[str, Decimal] = {}
        self._average_entry: dict[str, Decimal] = {}
        self._trades: list[Trade] = []

    def record_trade(self, trade: Trade) -> Trade:
        if trade.quantity <= 0 or trade.price <= 0:
            raise ValueError("Invalid trade quantity or price")
        self._trades.append(trade)
        fee = trade.fee.quantize(Decimal("0.00000001"))
        if trade.side.value == "buy":
            cost = (trade.quantity * trade.price + fee).quantize(Decimal("0.00000001"))
            if cost > self.cash:
                raise ValueError("Insufficient cash")
            self.cash -= cost
            current = self._positions.get(trade.symbol, Decimal("0"))
            self._positions[trade.symbol] = current + trade.quantity
            prev_qty = self._positions.get(trade.symbol, Decimal("0")) - trade.quantity
            if prev_qty > 0:
                prev_avg = self._average_entry[trade.symbol]
                total = prev_qty * prev_avg + trade.quantity * trade.price
                new_qty = prev_qty + trade.quantity
                self._average_entry[trade.symbol] = (total / new_qty).quantize(Decimal("0.00000001"))
            else:
                self._average_entry[trade.symbol] = trade.price
        elif trade.side.value == "sell":
            revenue = (trade.quantity * trade.price - fee).quantize(Decimal("0.00000001"))
            self.cash += revenue
            current = self._positions.get(trade.symbol, Decimal("0"))
            if trade.quantity > current:
                raise ValueError("Insufficient position")
            self._positions[trade.symbol] = current - trade.quantity
            if self._positions[trade.symbol] == 0:
                del self._positions[trade.symbol]
                del self._average_entry[trade.symbol]
        logger.info("Ledger trade recorded: %s %s %s @ %s", trade.side.value, trade.quantity, trade.symbol, trade.price)
        return trade

    def get_positions(self) -> list[dict]:
        result = []
        for symbol, qty in self._positions.items():
            if qty > 0:
                result.append({
                    "symbol": symbol,
                    "quantity": float(qty),
                    "average_entry_price": float(self._average_entry.get(symbol, Decimal("0"))),
                    "asset_class": self.asset_class.value,
                })
        return result

    def get_trades(self) -> list[dict]:
        return [
            {
                "id": t.id,
                "symbol": t.symbol,
                "side": t.side.value,
                "quantity": float(t.quantity),
                "price": float(t.price),
                "fee": float(t.fee),
                "timestamp": t.timestamp.isoformat(),
                "pnl": float(t.pnl),
                "asset_class": t.asset_class.value,
            }
            for t in self._trades
        ]

    def get_total_value(self, current_prices: Optional[dict[str, Decimal]] = None) -> Decimal:
        total = self.cash
        if current_prices:
            for symbol, qty in self._positions.items():
                if symbol in current_prices:
                    total += qty * current_prices[symbol]
        return total
