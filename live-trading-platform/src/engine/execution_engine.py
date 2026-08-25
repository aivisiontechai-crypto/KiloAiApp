from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Order, OrderStatus, OrderType, Side, TimeInForce, Trade
from src.portfolio.ledger import AssetLedger

logger = logging.getLogger(__name__)


class ExecutionEngine:
    def __init__(self, portfolio) -> None:
        self._portfolio = portfolio
        self._orders: dict[str, Order] = {}
        self._client_order_index: dict[str, Order] = {}
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
        time_in_force: TimeInForce = TimeInForce.GTC,
        client_order_id: Optional[str] = None,
        parent_order_id: Optional[str] = None,
        metadata: Optional[dict] = None,
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

        now = datetime.utcnow()
        coid = client_order_id or str(uuid.uuid4())
        order = Order(
            id=str(self._next_order_id),
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            status=OrderStatus.PENDING,
            timestamp=now,
            filled_quantity=Decimal("0"),
            average_fill_price=price,
            asset_class=asset_class,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_amount=trail_amount,
            trail_percent=trail_percent,
            parent_order_id=parent_order_id,
            time_in_force=time_in_force,
            expires_at=now + timedelta(hours=24) if time_in_force == TimeInForce.GTD else None,
            client_order_id=coid,
            metadata=metadata or {},
        )
        self._next_order_id += 1
        self._orders[order.id] = order
        self._client_order_index[coid] = order
        self._emit_order(order)
        if order_type == OrderType.MARKET and price is not None:
            self._execute_market_order(order, price)
        return order

    def submit_bracket_order(
        self,
        symbol: str,
        side: Side,
        quantity: Decimal,
        entry_price: Optional[Decimal],
        take_profit: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
        asset_class: AssetClass = AssetClass.CRYPTO,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> Optional[Order]:
        parent = self.submit_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=OrderType.LIMIT if entry_price else OrderType.MARKET,
            price=entry_price,
            asset_class=asset_class,
            time_in_force=time_in_force,
            metadata={"bracket": True},
        )
        if not parent:
            return None
        exit_side = Side.SELL if side == Side.BUY else Side.BUY
        tp_order = self.submit_order(
            symbol=symbol,
            side=exit_side,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            limit_price=take_profit,
            asset_class=asset_class,
            parent_order_id=parent.id,
            time_in_force=time_in_force,
            metadata={"bracket": True, "bracket_role": "take_profit"},
        )
        sl_order = self.submit_order(
            symbol=symbol,
            side=exit_side,
            quantity=quantity,
            order_type=OrderType.STOP_LOSS,
            stop_price=stop_loss,
            asset_class=asset_class,
            parent_order_id=parent.id,
            time_in_force=time_in_force,
            metadata={"bracket": True, "bracket_role": "stop_loss"},
        )
        parent.child_order_ids = []
        if tp_order:
            parent.child_order_ids.append(tp_order.id)
        if sl_order:
            parent.child_order_ids.append(sl_order.id)
        self._emit_order(parent)
        return parent

    def submit_oco(
        self,
        symbol: str,
        side: Side,
        quantity: Decimal,
        limit_order: Optional[dict] = None,
        stop_order: Optional[dict] = None,
        asset_class: AssetClass = AssetClass.CRYPTO,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> Optional[Order]:
        if not limit_order and not stop_order:
            return None
        oco_id = str(uuid.uuid4())
        orders = []
        if limit_order:
            o = self.submit_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=OrderType.LIMIT,
                limit_price=limit_order.get("limit_price"),
                asset_class=asset_class,
                time_in_force=time_in_force,
                metadata={"oco_id": oco_id, "oco_role": "limit"},
            )
            if o:
                orders.append(o)
        if stop_order:
            o = self.submit_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=OrderType.STOP_LIMIT,
                stop_price=stop_order.get("stop_price"),
                limit_price=stop_order.get("limit_price"),
                asset_class=asset_class,
                time_in_force=time_in_force,
                metadata={"oco_id": oco_id, "oco_role": "stop"},
            )
            if o:
                orders.append(o)
        for o in orders:
            o.metadata["oco_id"] = oco_id
        return orders[0] if orders else None

    def cancel_order(self, order_id: str) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        if order.status not in (OrderStatus.PENDING,):
            return False
        order.status = OrderStatus.CANCELLED
        self._emit_order(order)
        logger.info("Order cancelled: %s", order_id)
        return True

    def modify_order(self, order_id: str, limit_price: Optional[Decimal] = None, stop_price: Optional[Decimal] = None, quantity: Optional[Decimal] = None) -> Optional[Order]:
        order = self._orders.get(order_id)
        if not order:
            return None
        if order.status not in (OrderStatus.PENDING,):
            return None
        if limit_price is not None:
            order.limit_price = limit_price
        if stop_price is not None:
            order.stop_price = stop_price
        if quantity is not None and quantity > 0:
            order.quantity = quantity
        order.status = OrderStatus.REPLACED
        self._emit_order(order)
        order.status = OrderStatus.PENDING
        logger.info("Order modified: %s", order_id)
        return order

    def get_order(self, order_id: str) -> Optional[dict]:
        order = self._orders.get(order_id)
        if not order:
            return None
        return self._order_to_dict(order)

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
            if order.metadata.get("bracket"):
                self._cancel_children(order.id)
        except ValueError as exc:
            order.status = OrderStatus.REJECTED
            self._emit_order(order)
            logger.error("Order rejected: %s", exc)

    def _cancel_children(self, parent_id: str) -> None:
        for order in list(self._orders.values()):
            if order.parent_order_id == parent_id and order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CANCELLED
                self._emit_order(order)

    def _order_to_dict(self, order: Order) -> dict:
        return {
            "id": order.id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": float(order.quantity),
            "filled": float(order.filled_quantity),
            "status": order.status.value,
            "timestamp": order.timestamp.isoformat(),
            "order_type": order.order_type.value,
            "limit_price": float(order.limit_price) if order.limit_price else None,
            "stop_price": float(order.stop_price) if order.stop_price else None,
            "time_in_force": order.time_in_force.value,
            "parent_order_id": order.parent_order_id,
            "child_order_ids": order.child_order_ids,
            "client_order_id": order.client_order_id,
        }

    def get_active_orders(self) -> list[dict]:
        return [self._order_to_dict(o) for o in self._orders.values() if o.status in (OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED)]

    def get_order_history(self) -> list[dict]:
        return [self._order_to_dict(o) for o in self._orders.values()]

    def _emit_order(self, order: Order) -> None:
        for cb in list(self._order_callbacks):
            try:
                cb(order)
            except Exception as exc:
                logger.error("Order callback error: %s", exc)
