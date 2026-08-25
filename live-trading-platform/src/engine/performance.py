from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

import numpy as np

from src.data.models import Trade

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    total_return: float = 0.0
    annualized_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    metadata: dict = field(default_factory=dict)


class PerformanceAttribution:
    def __init__(self, risk_free_rate: float = 0.05) -> None:
        self.risk_free_rate = risk_free_rate

    def calculate_metrics(self, trades: list[Trade], equity_curve: list[float] = None) -> PerformanceMetrics:
        if not trades:
            return PerformanceMetrics()

        pnls = [float(t.pnl) for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]

        total_trades = len(trades)
        winning_trades = len(wins)
        losing_trades = len(losses)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        total_pnl = sum(pnls)
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = abs(np.mean(losses)) if losses else 0.0
        profit_factor = (sum(wins) / abs(sum(losses))) if losses else float("inf")

        max_dd = 0.0
        if equity_curve and len(equity_curve) > 1:
            peak = np.maximum.accumulate(equity_curve)
            drawdowns = (peak - equity_curve) / (peak + 1e-9)
            max_dd = float(np.max(drawdowns))

        returns = np.diff(equity_curve) / (np.array(equity_curve[:-1]) + 1e-9) if equity_curve and len(equity_curve) > 1 else np.array([0.0])
        sharpe = float(np.mean(returns) / (np.std(returns) + 1e-9)) if len(returns) > 0 else 0.0

        downside_returns = returns[returns < 0]
        sortino = float(np.mean(returns) / (np.std(downside_returns) + 1e-9)) if len(downside_returns) > 0 else 0.0

        calmar = float(np.mean(returns) / (max_dd + 1e-9)) if max_dd > 0 else 0.0

        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        for pnl in pnls:
            if pnl > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

        return PerformanceMetrics(
            total_return=total_pnl,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            max_drawdown=max_dd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
        )

    def calculate_attribution(self, trades: list[Trade], benchmark_returns: list[float] = None) -> dict:
        metrics = self.calculate_metrics(trades)
        attribution = {
            "total_pnl": metrics.total_return,
            "sharpe_ratio": metrics.sharpe_ratio,
            "sortino_ratio": metrics.sortino_ratio,
            "max_drawdown": metrics.max_drawdown,
            "win_rate": metrics.win_rate,
            "profit_factor": metrics.profit_factor,
            "avg_win": metrics.avg_win,
            "avg_loss": metrics.avg_loss,
            "total_trades": metrics.total_trades,
            "winning_trades": metrics.winning_trades,
            "losing_trades": metrics.losing_trades,
        }
        if benchmark_returns and len(benchmark_returns) > 1:
            strategy_returns = [float(t.pnl) / 100000.0 for t in trades]
            alpha = float(np.mean(strategy_returns) - np.mean(benchmark_returns))
            attribution["alpha"] = alpha
        return attribution
