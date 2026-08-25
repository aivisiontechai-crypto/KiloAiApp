from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from src.data.models import AssetClass, Trade

logger = logging.getLogger(__name__)


@dataclass
class TradeJournalEntry:
    trade: Trade
    strategy: str = ""
    signal_confidence: float = 0.0
    notes: str = ""
    tags: list[str] = field(default_factory=list)


class ReportingEngine:
    def __init__(self, portfolio) -> None:
        self.portfolio = portfolio
        self._journal: list[TradeJournalEntry] = []

    def add_journal_entry(self, trade: Trade, strategy: str = "", confidence: float = 0.0, notes: str = "", tags: list[str] = None) -> None:
        entry = TradeJournalEntry(
            trade=trade,
            strategy=strategy,
            signal_confidence=confidence,
            notes=notes,
            tags=tags or [],
        )
        self._journal.append(entry)

    def get_trade_journal(self, symbol: Optional[str] = None, strategy: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> list[dict]:
        entries = self._journal
        if symbol:
            entries = [e for e in entries if e.trade.symbol == symbol]
        if strategy:
            entries = [e for e in entries if e.strategy == strategy]
        if start_date:
            entries = [e for e in entries if e.trade.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.trade.timestamp <= end_date]
        return [
            {
                "id": e.trade.id,
                "timestamp": e.trade.timestamp.isoformat(),
                "symbol": e.trade.symbol,
                "side": e.trade.side.value,
                "quantity": float(e.trade.quantity),
                "price": float(e.trade.price),
                "fee": float(e.trade.fee),
                "pnl": float(e.trade.pnl),
                "strategy": e.strategy,
                "confidence": e.signal_confidence,
                "notes": e.notes,
                "tags": e.tags,
            }
            for e in entries
        ]

    def export_trades_csv(self, symbol: Optional[str] = None) -> str:
        entries = self.get_trade_journal(symbol=symbol)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "Symbol", "Side", "Quantity", "Price", "Fee", "PnL", "Strategy", "Notes", "Tags"])
        for e in entries:
            writer.writerow([
                e["id"],
                e["timestamp"],
                e["symbol"],
                e["side"],
                e["quantity"],
                e["price"],
                e["fee"],
                e["pnl"],
                e["strategy"],
                e["notes"],
                ", ".join(e["tags"]),
            ])
        return output.getvalue()

    def get_daily_pnl(self, days: int = 30) -> list[dict]:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        daily = {}
        for ac, trade_list in self.portfolio.get_trades().items():
            for t in trade_list:
                ts = datetime.fromisoformat(t["timestamp"])
                if start <= ts <= end:
                    day = ts.date().isoformat()
                    if day not in daily:
                        daily[day] = {"date": day, "realized_pnl": 0.0, "trades": 0}
                    daily[day]["realized_pnl"] += t["pnl"]
                    daily[day]["trades"] += 1
        return sorted(daily.values(), key=lambda x: x["date"])

    def get_tax_report(self, year: int = 2026) -> dict:
        trades = []
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        for ac, trade_list in self.portfolio.get_trades().items():
            for t in trade_list:
                ts = datetime.fromisoformat(t["timestamp"])
                if start <= ts <= end and t["side"] == "sell":
                    trades.append(t)
        total_gains = sum(t["pnl"] for t in trades if t["pnl"] > 0)
        total_losses = sum(abs(t["pnl"]) for t in trades if t["pnl"] < 0)
        return {
            "year": year,
            "total_trades": len(trades),
            "total_gains": total_gains,
            "total_losses": total_losses,
            "net_pnl": total_gains - total_losses,
        }
