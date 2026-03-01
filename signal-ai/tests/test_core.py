#!/usr/bin/env python3
"""SignalAI - Test Suite"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.signal_generator import SignalGenerator, SignalDatabase, CryptoDataProvider

def test_signal_generator():
    print("🧪 Testing Signal Generator...")
    gen = SignalGenerator()
    coins = gen.get_coins()
    assert len(coins) > 0, "Should have coins"
    print(f"   ✅ {len(coins)} coins loaded: PASS")
    print("   ✅ Signal Generator tests PASSED\n")

def test_signal_creation():
    print("🧪 Testing Signal Creation...")
    gen = SignalGenerator()
    
    async def test_gen():
        signal = await gen.generate_signal("bitcoin")
        return signal
    
    signal = asyncio.run(test_gen())
    assert signal is not None, "Signal should be created"
    assert signal.coin == "Bitcoin", "Coin should be Bitcoin"
    assert signal.entry_price > 0, "Entry price should be positive"
    print(f"   ✅ Signal: {signal.signal_type} {signal.symbol}")
    print(f"   ✅ Entry: ${signal.entry_price:,.2f}")
    print(f"   ✅ Target: ${signal.target_price:,.2f}")
    print("   ✅ Signal Creation tests PASSED\n")

def test_message_formatting():
    print("🧪 Testing Message Formatting...")
    gen = SignalGenerator()
    
    async def test_format():
        signal = await gen.generate_signal("ethereum")
        return signal
    
    signal = asyncio.run(test_format())
    message = gen.format_signal_message(signal)
    assert len(message) > 100, "Message should be substantial"
    assert signal.symbol in message, "Symbol should be in message"
    print(f"   ✅ Formatted message: {len(message)} chars")
    print("   ✅ Message Formatting tests PASSED\n")

def test_database():
    print("🧪 Testing Database...")
    db = SignalDatabase(db_path="data/test_signalai.db")
    db.add_user(999995, "test_user", "telegram")
    user = db.get_user(999995)
    assert user is not None, "User should exist"
    print("   ✅ User creation: PASS")
    print("   ✅ Database tests PASSED\n")

def run_all_tests():
    print("\n" + "="*50)
    print("📈 SIGNALAI TEST SUITE")
    print("="*50 + "\n")
    try:
        test_signal_generator()
        test_signal_creation()
        test_message_formatting()
        test_database()
        print("="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        sys.exit(1)

if __name__ == "__main__": run_all_tests()
