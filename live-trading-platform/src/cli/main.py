from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.adapters.kraken_adapter import KrakenAdapter
from src.data.manager import DataManager
from src.data.models import AssetClass
from src.engine.autonomous_trader import AutonomousTrader, RiskManager
from src.engine.execution_engine import ExecutionEngine
from src.portfolio.portfolio import Portfolio
from src.self_improvement.engine import SelfImprovementEngine
from src.self_improvement.health_monitor import StrategyHealthMonitor
from src.strategies.momentum_strategy import MomentumStrategy
from src.strategies.strategies import MovingAverageCrossover

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Live Trading Platform CLI")
    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start", help="Start trading platform")
    start_parser.add_argument("--symbols", nargs="+", default=["BTC-USD"])
    start_parser.add_argument("--capital", type=float, default=50000)

    subparsers.add_parser("status", help="Show platform status")
    subparsers.add_parser("portfolio", help="Show portfolio")
    subparsers.add_parser("performance", help="Show performance")
    subparsers.add_parser("rollback", help="Rollback strategy")

    args = parser.parse_args()
    if args.command == "start":
        data_manager = DataManager()
        adapter = KrakenAdapter(args.symbols)
        data_manager.register_adapter(adapter)
        portfolio = Portfolio({AssetClass.CRYPTO: (args.capital, "USD")})
        engine = ExecutionEngine(portfolio)
        risk_manager = RiskManager()
        strategies = [
            MovingAverageCrossover(name="MA_Crossover", asset_class=AssetClass.CRYPTO, symbols=args.symbols, parameters={"fast_period": 10, "slow_period": 30}),
            MomentumStrategy(name="Momentum", asset_class=AssetClass.CRYPTO, symbols=args.symbols, parameters={"roc_period": 14, "threshold": 0.02}),
        ]
        trader = AutonomousTrader(data_manager, portfolio, engine, strategies, risk_manager)
        health_monitor = StrategyHealthMonitor()
        improvement_engine = SelfImprovementEngine(health_monitor=health_monitor)
        for s in strategies:
            improvement_engine.register_strategy(s)
        import asyncio
        asyncio.run(trader.start())
        asyncio.run(data_manager.start())
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            asyncio.run(trader.stop())
            asyncio.run(data_manager.stop())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
