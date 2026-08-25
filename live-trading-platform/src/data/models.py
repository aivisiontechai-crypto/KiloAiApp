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
    BRACKET = "bracket"
    OCO = "oco"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    PEGGED = "pegged"
    MARKET_IF_TOUCHED = "market_if_touched"
    LIMIT_IF_TOUCHED = "limit_if_touched"


class OrderStatus(str, Enum):
    NEW = "new"
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REPLACED = "replaced"


class TimeInForce(str, Enum):
    GTC = "gtc"
    GTD = "gtd"
    IOC = "ioc"
    FOK = "fok"
    DAY = "day"


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
    child_order_ids: list[str] = field(default_factory=list)
    time_in_force: TimeInForce = TimeInForce.GTC
    expires_at: Optional[datetime] = None
    client_order_id: Optional[str] = None
    replaced_by: Optional[str] = None
    metadata: dict = field(default_factory=dict)


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


@dataclass
class OrderTicket:
    symbol: str
    side: Side
    quantity: Decimal
    order_type: OrderType
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    client_order_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ScanResult:
    symbol: str
    signal: str
    confidence: float
    indicator_values: dict
    timestamp: datetime
    asset_class: AssetClass = AssetClass.CRYPTO


@dataclass
class TimeSales:
    symbol: str
    price: Decimal
    quantity: Decimal
    side: Side
    timestamp: datetime
    exchange: str = ""
    asset_class: AssetClass = AssetClass.CRYPTO


@dataclass
class DrawingTool:
    id: str
    tool_type: str
    symbol: str
    points: list[dict]
    color: str = "#00d4ff"
    metadata: dict = field(default_factory=dict)


@dataclass
class Webhook:
    id: str
    url: str
    events: list[str]
    secret: str = ""
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccountStatement:
    account_id: str
    asset_class: AssetClass
    start_date: datetime
    end_date: datetime
    opening_cash: Decimal
    closing_cash: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_fees: Decimal
    trades: list[dict] = field(default_factory=list)
