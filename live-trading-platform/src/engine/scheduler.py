from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Order, OrderStatus, OrderType, Side, TimeInForce

logger = logging.getLogger(__name__)


class ScheduledOrder:
    def __init__(self, order: Order, execute_at: datetime, recurring: bool = False, interval_seconds: Optional[int] = None):
        self.id = str(uuid.uuid4())
        self.order = order
        self.execute_at = execute_at
        self.recurring = recurring
        self.interval_seconds = interval_seconds
        self.cancelled = False

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order.id,
            "symbol": self.order.symbol,
            "side": self.order.side.value,
            "quantity": str(self.order.quantity),
            "order_type": self.order.order_type.value,
            "execute_at": self.execute_at.isoformat(),
            "recurring": self.recurring,
            "interval_seconds": self.interval_seconds,
            "cancelled": self.cancelled,
        }


class TradeScheduler:
    def __init__(self, execution_engine):
        self._engine = execution_engine
        self._scheduled: dict[str, ScheduledOrder] = {}
        self._running = False
        self._task = None

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def schedule_order(
        self,
        symbol: str,
        side: Side,
        quantity: Decimal,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        asset_class: AssetClass = AssetClass.CRYPTO,
        execute_at: Optional[datetime] = None,
        recurring: bool = False,
        interval_seconds: Optional[int] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> ScheduledOrder:
        if execute_at is None:
            execute_at = datetime.utcnow()

        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            status=OrderStatus.PENDING,
            timestamp=datetime.utcnow(),
            limit_price=limit_price,
            stop_price=stop_price,
            asset_class=asset_class,
            time_in_force=time_in_force,
        )

        scheduled = ScheduledOrder(order, execute_at, recurring, interval_seconds)
        self._scheduled[scheduled.id] = scheduled
        return scheduled

    def cancel_scheduled(self, scheduled_id: str) -> bool:
        if scheduled_id in self._scheduled:
            self._scheduled[scheduled_id].cancelled = True
            del self._scheduled[scheduled_id]
            return True
        return False

    def get_scheduled(self) -> list[dict]:
        return [s.to_dict() for s in self._scheduled.values()]

    async def _run_loop(self):
        while self._running:
            try:
                now = datetime.utcnow()
                to_remove = []
                for sid, scheduled in list(self._scheduled.items()):
                    if scheduled.cancelled:
                        to_remove.append(sid)
                        continue
                    if now >= scheduled.execute_at:
                        try:
                            scheduled.order.status = OrderStatus.NEW
                            self._engine._orders[scheduled.order.id] = scheduled.order
                            if scheduled.recurring and scheduled.interval_seconds:
                                scheduled.execute_at = now + timedelta(seconds=scheduled.interval_seconds)
                            else:
                                to_remove.append(sid)
                        except Exception as exc:
                            logger.error("Scheduled order execution error: %s", exc)
                            to_remove.append(sid)
                for sid in to_remove:
                    self._scheduled.pop(sid, None)
                await asyncio.sleep(1)
            except Exception as exc:
                logger.error("Scheduler loop error: %s", exc)
                await asyncio.sleep(1)
