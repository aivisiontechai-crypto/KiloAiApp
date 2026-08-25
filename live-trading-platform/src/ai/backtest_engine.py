from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

import numpy as np

from src.data.models import AssetClass, Candle
from src.portfolio.ledger import AssetLedger

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades: int
    equity_curve: list[float] = field(default_factory=list)


class BacktestEngine:
    def __init__(self, initial_capital: Decimal = Decimal("100000"), fee_rate: float = 0.001, slippage: float = 0.0005) -> None:
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self.slippage = slippage

    def run_backtest(self, strategy, candles: list[Candle], asset_class: AssetClass) -> BacktestResult:
        ledger = AssetLedger(asset_class, self.initial_capital, "USD")
        equity = [float(self.initial_capital)]
        trades = 0
        wins = 0
        for i in range(1, len(candles)):
            candle = candles[i]
            signal = strategy.on_candle(candle)
            if signal:
                fill_price = candle.close * (Decimal("1") + Decimal(str(self.slippage)))
                qty = Decimal("0.01")
                try:
                    from src.data.models import Trade
                    trade = Trade(
                        id=str(trades),
                        symbol=candle.symbol,
                        side=signal.side,
                        quantity=qty,
                        price=fill_price,
                        fee=(fill_price * qty * Decimal(str(self.fee_rate))).quantize(Decimal("0.00000001")),
                        timestamp=candle.timestamp,
                        asset_class=asset_class,
                    )
                    ledger.record_trade(trade)
                    trades += 1
                    if signal.side.value == "sell":
                        wins += 1
                except ValueError:
                    pass
            total = ledger.get_total_value({candle.symbol: candle.close})
            equity.append(float(total))
        returns = np.diff(equity) / (np.array(equity[:-1]) + 1e-9)
        sharpe = float(np.mean(returns) / (np.std(returns) + 1e-9)) if len(returns) > 0 else 0.0
        peak = np.maximum.accumulate(equity)
        drawdowns = (peak - equity) / (peak + 1e-9)
        max_dd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0
        win_rate = wins / trades if trades > 0 else 0.0
        return BacktestResult(
            total_return=(equity[-1] - equity[0]) / equity[0],
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
            trades=trades,
            equity_curve=equity,
        )
