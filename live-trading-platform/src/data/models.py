from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class AssetClass(str, Enum):
    CRYPTO = "crypto"
    US_EQUITY = "us_equity"


@dataclass
class Price:
    symbol: str
    value: Decimal
    timestamp: datetime
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    asset_class: AssetClass = AssetClass.CRYPTO


@dataclass
class Trade:
    id: str
    symbol: str
    side: Side
    quantity: Decimal
    price: Decimal
    fee: Decimal
    timestamp: datetime
    asset_class: AssetClass


@dataclass
class Candle:
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    asset_class: AssetClass = AssetClass.CRYPTO


@dataclass
class Position:
    symbol: str
    quantity: Decimal
    average_entry_price: Decimal
    current_price: Optional[Decimal] = None
    asset_class: AssetClass = AssetClass.CRYPTO

    @property
    def market_value(self) -> Optional[Decimal]:
        if self.current_price is None:
            return None
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> Optional[Decimal]:
        if self.current_price is None:
            return None
        return (self.current_price - self.average_entry_price) * self.quantity


@dataclass
class LedgerEntry:
    timestamp: datetime
    symbol: str
    side: Side
    quantity: Decimal
    price: Decimal
    fee: Decimal
    pnl: Decimal = Decimal("0")
    asset_class: AssetClass = AssetClass.CRYPTO


@dataclass
class Order:
    id: str
    symbol: str
    side: Side
    quantity: Decimal
    order_type: OrderType
    status: OrderStatus
    timestamp: datetime
    filled_quantity: Decimal = Decimal("0")
    average_fill_price: Optional[Decimal] = None
    asset_class: AssetClass = AssetClass.CRYPTO
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    trail_amount: Optional[Decimal] = None
    trail_percent: Optional[float] = None
    parent_order_id: Optional[str] = None


@dataclass
class OrderBookLevel:
    price: Decimal
    quantity: Decimal
    order_count: int = 0


@dataclass
class OrderBook:
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: datetime
    asset_class: AssetClass = AssetClass.CRYPTO


@dataclass
class RiskMetrics:
    symbol: str
    var_95: float = 0.0
    var_99: float = 0.0
    margin_requirement: float = 0.0
    leverage: float = 1.0
    stress_test_loss: float = 0.0
    beta: float = 1.0
    correlation: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class NewsItem:
    id: str
    symbol: str
    title: str
    source: str
    sentiment: float
    timestamp: datetime
    url: str = ""


@dataclass
class StrategySignal:
    symbol: str
    side: Side
    confidence: float
    strategy: str
    metadata: dict = field(default_factory=dict)
