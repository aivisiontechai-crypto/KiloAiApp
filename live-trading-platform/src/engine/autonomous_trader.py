from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.data.manager import DataManager
from src.data.models import AssetClass, Candle, Price, Side
from src.engine.alerts import AlertManager
from src.engine.execution_engine import ExecutionEngine
from src.engine.news import NewsSentimentEngine
from src.engine.risk import RiskAnalyzer
from src.engine.watchlist import WatchlistManager
from src.portfolio.ledger import AssetLedger
from src.portfolio.portfolio import Portfolio
from src.self_improvement.engine import SelfImprovementEngine
from src.self_improvement.health_monitor import StrategyHealthMonitor
from src.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class RiskManager:
    def __init__(self, max_position_size: Decimal = Decimal("0.1"), max_open_orders: int = 10, max_loss_per_trade: Decimal = Decimal("0.02")) -> None:
        self.max_position_size = max_position_size
        self.max_open_orders = max_open_orders
        self.max_loss_per_trade = max_loss_per_trade
        self._open_orders = 0

    def check_order(self, symbol: str, ledger: AssetLedger, price: Price, side: Side = Side.BUY, quantity: Decimal = Decimal("0.01")) -> bool:
        if self._open_orders >= self.max_open_orders:
            logger.warning("Risk: max open orders reached")
            return False
        if side == Side.BUY:
            cost = quantity * price.value
            if cost > ledger.cash * self.max_position_size:
                logger.warning("Risk: position size limit for %s", symbol)
                return False
            if cost > ledger.cash:
                logger.warning("Risk: insufficient cash for %s", symbol)
                return False
        elif side == Side.SELL:
            positions = ledger.get_positions()
            pos = next((p for p in positions if p["symbol"] == symbol), None)
            if not pos or pos["quantity"] < float(quantity):
                logger.warning("Risk: insufficient position for %s", symbol)
                return False
        return True

    def increment(self) -> None:
        self._open_orders += 1

    def decrement(self) -> None:
        if self._open_orders > 0:
            self._open_orders -= 1


class AutonomousTrader:
    def __init__(self, data_manager: DataManager, portfolio: Portfolio, engine: ExecutionEngine, strategies: list[BaseStrategy], risk_manager: RiskManager, improvement_engine: Optional[SelfImprovementEngine] = None, health_monitor: Optional[StrategyHealthMonitor] = None, alert_manager: Optional[AlertManager] = None, watchlist_manager: Optional[WatchlistManager] = None, risk_analyzer: Optional[RiskAnalyzer] = None, news_engine: Optional[NewsSentimentEngine] = None) -> None:
        self.data_manager = data_manager
        self.portfolio = portfolio
        self.engine = engine
        self.strategies = strategies
        self.risk_manager = risk_manager
        self.improvement_engine = improvement_engine
        self.health_monitor = health_monitor
        self.alert_manager = alert_manager
        self.watchlist_manager = watchlist_manager
        self.risk_analyzer = risk_analyzer
        self.news_engine = news_engine
        self._last_price: dict[str, Price] = {}
        self._previous_price: dict[str, Price] = {}
        self._signal_counts: dict[str, datetime] = {}
        self._running = False
        self._improvement_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._running = True
        self._improvement_task = asyncio.create_task(self._continuous_improvement_loop())
        logger.info("Autonomous trader started")

    async def stop(self) -> None:
        self._running = False
        if self._improvement_task:
            self._improvement_task.cancel()
            try:
                await self._improvement_task
            except asyncio.CancelledError:
                pass
        logger.info("Autonomous trader stopped")

    async def _continuous_improvement_loop(self) -> None:
        while self._running:
            try:
                if self.improvement_engine:
                    metrics = self._collect_metrics()
                    self.improvement_engine.evaluate_and_improve(metrics)
                    self.improvement_engine.auto_rollback_unhealthy()
                await asyncio.sleep(300)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Improvement loop error: %s", exc)
                await asyncio.sleep(300)

    def _collect_metrics(self) -> dict:
        metrics = {}
        for strategy in self.strategies:
            trades = []
            for ac, trade_list in self.portfolio.get_trades().items():
                for t in trade_list:
                    if t.get("asset_class") == strategy.asset_class.value:
                        trades.append(t)
            pnl = sum((Decimal(str(t["price"])) * Decimal(str(t["quantity"]))) for t in trades if t["side"] == "sell")
            metrics[strategy.name] = {
                "trades": len(trades),
                "pnl": float(pnl),
                "win_rate": 0.5,
                "drawdown": 0.0,
            }
        return metrics

    def process_signals(self) -> None:
        if not self._running:
            return
        for strategy in self.strategies:
            for symbol in strategy.symbols:
                candles = self.data_manager.get_adapter(strategy.asset_class)
                if candles is None:
                    continue
                try:
                    price = self._last_price.get(symbol)
                    if not price:
                        continue
                    signal = strategy.on_candle(None)
                    if signal:
                        if not self._cooldown_ok(symbol):
                            continue
                        ledger = self.portfolio.get_ledger(price.asset_class)
                        if not self.risk_manager.check_order(signal.symbol, ledger, price, signal.side):
                            continue
                        order = self.engine.submit_order(
                            symbol=signal.symbol,
                            side=signal.side,
                            quantity=Decimal("0.01"),
                            asset_class=price.asset_class,
                            price=price.value,
                        )
                        if order:
                            self.risk_manager.increment()
                            if self.health_monitor:
                                self.health_monitor.record_trade(strategy.name, Decimal("0"), float(ledger.get_total_value()))
                except Exception as exc:
                    logger.error("Signal processing error: %s", exc)

    def _cooldown_ok(self, symbol: str, cooldown_seconds: int = 60) -> bool:
        last = self._signal_counts.get(symbol)
        if last is None:
            return True
        return (datetime.utcnow() - last).total_seconds() >= cooldown_seconds

    def update_price(self, price: Price) -> None:
        previous_price = self._last_price.get(price.symbol)
        self._previous_price[price.symbol] = previous_price
        self._last_price[price.symbol] = price
        if self.alert_manager:
            try:
                self.alert_manager.check_price_alert(price.symbol, price.value, previous_price.value if previous_price else None)
            except Exception as exc:
                logger.error("Alert check error: %s", exc)

    def deploy_strategy(self, name: str, parameters: dict) -> bool:
        for strategy in self.strategies:
            if strategy.name == name:
                strategy.parameters.update(parameters)
                logger.info("Deployed new parameters to %s: %s", name, parameters)
                return True
        return False

    def get_strategy_health(self) -> list[dict]:
        if not self.health_monitor:
            return []
        return [
            {"name": name, **metrics}
            for name, metrics in self.health_monitor._strategies.items()
        ]
