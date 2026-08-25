from __future__ import annotations

import unittest
from decimal import Decimal
from datetime import datetime, timezone

from src.data.models import AssetClass, OrderType, Side, Trade
from src.portfolio.ledger import AssetLedger
from src.strategies.strategies import MovingAverageCrossover
from src.strategies.momentum_strategy import MomentumStrategy


class TestLedger(unittest.TestCase):
    def test_buy_and_sell(self):
        ledger = AssetLedger(AssetClass.CRYPTO, Decimal("1000"), "USD")
        trade = Trade(id="1", symbol="BTC-USD", side=Side.BUY, quantity=Decimal("0.1"), price=Decimal("100"), fee=Decimal("0.1"), timestamp=datetime.now(timezone.utc), asset_class=AssetClass.CRYPTO)
        ledger.record_trade(trade)
        self.assertEqual(ledger.cash, Decimal("989.9"))
        positions = ledger.get_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["quantity"], 0.1)

    def test_insufficient_cash(self):
        ledger = AssetLedger(AssetClass.CRYPTO, Decimal("10"), "USD")
        trade = Trade(id="1", symbol="BTC-USD", side=Side.BUY, quantity=Decimal("1"), price=Decimal("100"), fee=Decimal("0.1"), timestamp=datetime.now(timezone.utc), asset_class=AssetClass.CRYPTO)
        with self.assertRaises(ValueError):
            ledger.record_trade(trade)


class TestStrategies(unittest.TestCase):
    def test_ma_crossover_buy(self):
        strategy = MovingAverageCrossover("test", AssetClass.CRYPTO, ["BTC-USD"], {"fast_period": 2, "slow_period": 3})
        prices = [Decimal("20"), Decimal("19"), Decimal("18"), Decimal("17"), Decimal("16"), Decimal("15")]
        for p in prices:
            strategy._prices["BTC-USD"].append(p)
        strategy.on_candle(None)
        strategy._prices["BTC-USD"].append(Decimal("30"))
        signal = strategy.on_candle(None)
        self.assertIsNotNone(signal)
        self.assertEqual(signal.side, Side.BUY)

    def test_momentum_buy(self):
        strategy = MomentumStrategy("test", AssetClass.CRYPTO, ["ETH-USD"], {"roc_period": 2, "threshold": 0.01})
        prices = [Decimal("100"), Decimal("101"), Decimal("103")]
        for p in prices:
            strategy._prices["ETH-USD"].append(p)
        signal = strategy.on_candle(None)
        self.assertIsNotNone(signal)
        self.assertEqual(signal.side, Side.BUY)


if __name__ == "__main__":
    unittest.main()
