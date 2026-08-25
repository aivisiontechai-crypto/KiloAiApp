from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    PRICE = "price"
    INDICATOR = "indicator"
    NEWS = "news"
    PORTFOLIO = "portfolio"


class AlertCondition(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    PERCENT_CHANGE = "percent_change"
    VOLUME_SPIKE = "volume_spike"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"
    EXPIRED = "expired"


@dataclass
class Alert:
    id: str
    alert_type: AlertType
    symbol: str
    condition: AlertCondition
    threshold: Decimal
    current_status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    triggered_at: Optional[datetime] = None
    message: str = ""
    metadata: dict = field(default_factory=dict)
    expires_at: Optional[datetime] = None


class AlertManager:
    def __init__(self) -> None:
        self._alerts: dict[str, Alert] = {}
        self._callbacks: list[Callable[[Alert], None]] = []
        self._next_id = 1

    def on_alert(self, callback: Callable[[Alert], None]) -> None:
        self._callbacks.append(callback)

    def create_price_alert(self, symbol: str, condition: AlertCondition, threshold: Decimal, message: str = "") -> Alert:
        alert = Alert(
            id=str(self._next_id),
            alert_type=AlertType.PRICE,
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            message=message or f"Price {condition.value} {threshold}",
        )
        self._next_id += 1
        self._alerts[alert.id] = alert
        logger.info("Created price alert %s for %s", alert.id, symbol)
        return alert

    def create_indicator_alert(self, symbol: str, condition: AlertCondition, threshold: Decimal, indicator_name: str, message: str = "") -> Alert:
        alert = Alert(
            id=str(self._next_id),
            alert_type=AlertType.INDICATOR,
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            message=message or f"{indicator_name} {condition.value} {threshold}",
            metadata={"indicator": indicator_name},
        )
        self._next_id += 1
        self._alerts[alert.id] = alert
        logger.info("Created indicator alert %s for %s", alert.id, symbol)
        return alert

    def check_price_alert(self, symbol: str, price: Decimal, previous_price: Optional[Decimal] = None) -> list[Alert]:
        triggered = []
        for alert in list(self._alerts.values()):
            if alert.symbol != symbol or alert.current_status != AlertStatus.ACTIVE:
                continue
            if alert.expires_at and datetime.utcnow() > alert.expires_at:
                alert.current_status = AlertStatus.EXPIRED
                continue
            triggered_flag = False
            if alert.condition == AlertCondition.ABOVE and price > alert.threshold:
                triggered_flag = True
            elif alert.condition == AlertCondition.BELOW and price < alert.threshold:
                triggered_flag = True
            elif alert.condition == AlertCondition.CROSSES_ABOVE and previous_price is not None and previous_price <= alert.threshold and price > alert.threshold:
                triggered_flag = True
            elif alert.condition == AlertCondition.CROSSES_BELOW and previous_price is not None and previous_price >= alert.threshold and price < alert.threshold:
                triggered_flag = True
            elif alert.condition == AlertCondition.PERCENT_CHANGE and previous_price is not None and previous_price > 0:
                pct_change = abs((price - previous_price) / previous_price) * Decimal("100")
                if pct_change >= alert.threshold:
                    triggered_flag = True
            if triggered_flag:
                alert.current_status = AlertStatus.TRIGGERED
                alert.triggered_at = datetime.utcnow()
                triggered.append(alert)
                for cb in self._callbacks:
                    try:
                        cb(alert)
                    except Exception as exc:
                        logger.error("Alert callback error: %s", exc)
        return triggered

    def check_indicator_alert(self, symbol: str, indicator_name: str, value: Decimal, signal: Optional[str] = None) -> list[Alert]:
        triggered = []
        for alert in list(self._alerts.values()):
            if alert.symbol != symbol or alert.current_status != AlertStatus.ACTIVE or alert.alert_type != AlertType.INDICATOR:
                continue
            if alert.metadata.get("indicator") != indicator_name:
                continue
            if alert.expires_at and datetime.utcnow() > alert.expires_at:
                alert.current_status = AlertStatus.EXPIRED
                continue
            if alert.condition == AlertCondition.ABOVE and value > alert.threshold:
                alert.current_status = AlertStatus.TRIGGERED
                alert.triggered_at = datetime.utcnow()
                triggered.append(alert)
            elif alert.condition == AlertCondition.BELOW and value < alert.threshold:
                alert.current_status = AlertStatus.TRIGGERED
                alert.triggered_at = datetime.utcnow()
                triggered.append(alert)
            if alert.current_status == AlertStatus.TRIGGERED:
                for cb in self._callbacks:
                    try:
                        cb(alert)
                    except Exception as exc:
                        logger.error("Alert callback error: %s", exc)
        return triggered

    def disable_alert(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.current_status = AlertStatus.DISABLED
            return True
        return False

    def delete_alert(self, alert_id: str) -> bool:
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            return True
        return False

    def get_active_alerts(self) -> list[Alert]:
        return [a for a in self._alerts.values() if a.current_status == AlertStatus.ACTIVE]

    def get_alerts_for_symbol(self, symbol: str) -> list[Alert]:
        return [a for a in self._alerts.values() if a.symbol == symbol]

    def get_all_alerts(self) -> list[Alert]:
        return list(self._alerts.values())
