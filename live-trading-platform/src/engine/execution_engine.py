from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Order, OrderStatus, OrderType, Side, Trade
from src.portfolio.ledger import AssetLedger

logger = logging.getLogger(__name__)


class ExecutionEngine:
    def __init__(self, portfolio) -> None:
        self._portfolio = portfolio
        self._orders: dict[str, Order] = {}
        self._fill_callbacks = []
        self._order_callbacks = []
        self._next_order_id = 1

    def on_fill(self, callback) -> None:
        self._fill_callbacks.append(callback)

    def on_order_update(self, callback) -> None:
        self._order_callbacks.append(callback)

    def submit_order(
        self,
        symbol: str,
        side: Side,
        quantity: Decimal,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[Decimal] = None,
        asset_class: AssetClass = AssetClass.CRYPTO,
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        trail_amount: Optional[Decimal] = None,
        trail_percent: Optional[float] = None,
    ) -> Optional[Order]:
        if quantity <= 0:
            logger.error("Rejected order: non-positive quantity %s", quantity)
            return None
        if order_type == OrderType.STOP_LOSS and stop_price is None:
            logger.error("Rejected STOP_LOSS order: stop_price required")
            return None
        if order_type == OrderType.STOP_LIMIT and (stop_price is None or limit_price is None):
            logger.error("Rejected STOP_LIMIT order: stop_price and limit_price required")
            return None
        if order_type == OrderType.TRAILING_STOP and trail_amount is None and trail_percent is None:
            logger.error("Rejected TRAILING_STOP order: trail_amount or trail_percent required")
            return None
        order = Order(
            id=str(self._next_order_id),
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            status=OrderStatus.PENDING,
            timestamp=datetime.utcnow(),
            filled_quantity=Decimal("0"),
            average_fill_price=price,
            asset_class=asset_class,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_amount=trail_amount,
            trail_percent=trail_percent,
        )
        self._next_order_id += 1
        self._orders[order.id] = order
        if order_type == OrderType.MARKET and price is not None:
            self._execute_market_order(order, price)
        elif order_type == OrderType.LIMIT:
            logger.info("LIMIT order %s queued at %s", order.id, limit_price)
        elif order_type == OrderType.STOP_LOSS:
            logger.info("STOP_LOSS order %s queued at %s", order.id, stop_price)
        elif order_type == OrderType.STOP_LIMIT:
            logger.info("STOP_LIMIT order %s queued: stop=%s, limit=%s", order.id, stop_price, limit_price)
        elif order_type == OrderType.TRAILING_STOP:
            logger.info("TRAILING_STOP order %s queued: trail_amount=%s, trail_percent=%s", order.id, trail_amount, trail_percent)
        self._emit_order(order)
        return order

    def _execute_market_order(self, order: Order, fill_price: Decimal) -> None:
        if fill_price <= 0:
            order.status = OrderStatus.REJECTED
            self._emit_order(order)
            logger.error("Order rejected: invalid fill price %s", fill_price)
            return
        ledger = self._portfolio.get_ledger(order.asset_class)
        fee = (order.quantity * fill_price * Decimal("0.001")).quantize(Decimal("0.00000001"))
        trade = Trade(
            id=order.id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            fee=fee,
            timestamp=datetime.utcnow(),
            asset_class=order.asset_class,
        )
        try:
            ledger.record_trade(trade)
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.average_fill_price = fill_price
            self._emit_order(order)
            for cb in self._fill_callbacks:
                try:
                    cb(order, trade)
                except Exception as exc:
                    logger.error("Fill callback error: %s", exc)
        except ValueError as exc:
            order.status = OrderStatus.REJECTED
            self._emit_order(order)
            logger.error("Order rejected: %s", exc)

    def get_active_orders(self) -> list[dict]:
        return [
            {
                "id": o.id,
                "symbol": o.symbol,
                "side": o.side.value,
                "quantity": float(o.quantity),
                "filled": float(o.filled_quantity),
                "status": o.status.value,
                "timestamp": o.timestamp.isoformat(),
                "order_type": o.order_type.value,
                "limit_price": float(o.limit_price) if o.limit_price else None,
                "stop_price": float(o.stop_price) if o.stop_price else None,
            }
            for o in self._orders.values()
            if o.status in (OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED)
        ]

    def get_order_history(self) -> list[dict]:
        return [
            {
                "id": o.id,
                "symbol": o.symbol,
                "side": o.side.value,
                "quantity": float(o.quantity),
                "filled": float(o.filled_quantity),
                "status": o.status.value,
                "timestamp": o.timestamp.isoformat(),
                "order_type": o.order_type.value,
                "limit_price": float(o.limit_price) if o.limit_price else None,
                "stop_price": float(o.stop_price) if o.stop_price else None,
            }
            for o in self._orders.values()
        ]

    def _emit_order(self, order: Order) -> None:
        for cb in list(self._order_callbacks):
            try:
                cb(order)
            except Exception as exc:
                logger.error("Order callback error: %s", exc)
