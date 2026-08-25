from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Trade

logger = logging.getLogger(__name__)


@dataclass
class Position:
    symbol: str
    quantity: Decimal
    average_entry_price: Decimal
    current_price: Optional[Decimal] = None
    asset_class: AssetClass = AssetClass.CRYPTO
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    cost_basis: Decimal = Decimal("0")
    market_value: Optional[Decimal] = None
    weight: float = 0.0
    metadata: dict = field(default_factory=dict)


class AssetLedger:
    def __init__(self, asset_class: AssetClass, cash: Decimal, currency: str = "USD") -> None:
        self.asset_class = asset_class
        self.cash = cash
        self.currency = currency
        self._positions: dict[str, Position] = {}
        self._trades: list[Trade] = []

    def record_trade(self, trade: Trade) -> Trade:
        if trade.quantity <= 0 or trade.price <= 0:
            raise ValueError("Invalid trade quantity or price")
        self._trades.append(trade)
        fee = trade.fee.quantize(Decimal("0.00000001"))
        symbol = trade.symbol

        if trade.side.value == "buy":
            cost = (trade.quantity * trade.price + fee).quantize(Decimal("0.00000001"))
            if cost > self.cash:
                raise ValueError("Insufficient cash")
            self.cash -= cost
            if symbol in self._positions:
                pos = self._positions[symbol]
                total_cost = pos.cost_basis + trade.quantity * trade.price
                new_qty = pos.quantity + trade.quantity
                pos.average_entry_price = (total_cost / new_qty).quantize(Decimal("0.00000001"))
                pos.quantity = new_qty
                pos.cost_basis = total_cost
            else:
                self._positions[symbol] = Position(
                    symbol=symbol,
                    quantity=trade.quantity,
                    average_entry_price=trade.price,
                    asset_class=trade.asset_class,
                    cost_basis=trade.quantity * trade.price,
                )
        elif trade.side.value == "sell":
            revenue = (trade.quantity * trade.price - fee).quantize(Decimal("0.00000001"))
            self.cash += revenue
            pos = self._positions.get(symbol)
            if not pos or trade.quantity > pos.quantity:
                raise ValueError("Insufficient position")
            pnl = (trade.price - pos.average_entry_price) * trade.quantity - fee
            pos.realized_pnl += pnl
            pos.quantity -= trade.quantity
            pos.cost_basis = pos.average_entry_price * pos.quantity
            if pos.quantity == 0:
                del self._positions[symbol]
        logger.info("Ledger trade recorded: %s %s %s @ %s", trade.side.value, trade.quantity, symbol, trade.price)
        return trade

    def get_positions(self) -> list[dict]:
        result = []
        for pos in self._positions.values():
            if pos.quantity > 0:
                result.append({
                    "symbol": pos.symbol,
                    "quantity": float(pos.quantity),
                    "average_entry_price": float(pos.average_entry_price),
                    "current_price": float(pos.current_price) if pos.current_price else None,
                    "asset_class": pos.asset_class.value,
                    "unrealized_pnl": float(pos.unrealized_pnl),
                    "realized_pnl": float(pos.realized_pnl),
                    "cost_basis": float(pos.cost_basis),
                    "market_value": float(pos.market_value) if pos.market_value else None,
                    "weight": pos.weight,
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
            for symbol, pos in self._positions.items():
                if symbol in current_prices:
                    total += pos.quantity * current_prices[symbol]
        return total

    def get_margin_requirement(self) -> Decimal:
        margin = Decimal("0")
        for pos in self._positions.values():
            if pos.current_price:
                margin += pos.quantity * pos.current_price
        return margin
