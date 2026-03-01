#!/usr/bin/env python3
"""CryptoAI News - Test Suite"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.news_generator import NewsAggregator, NewsDatabase, COIN_KEYWORDS

def test_news_aggregator():
    print("🧪 Testing News Aggregator...")
    agg = NewsAggregator()
    coins = list(COIN_KEYWORDS.keys())
    assert len(coins) > 0, "Should have coin categories"
    print(f"   ✅ {len(coins)} coins tracked: PASS")
    print("   ✅ News Aggregator tests PASSED\n")

def test_sentiment():
    print("🧪 Testing Sentiment Analysis...")
    agg = NewsAggregator()
    result = agg.sentiment.analyze("Bitcoin surges higher as bullish momentum continues")
    assert result["sentiment"] == "bullish", "Should be bullish"
    print(f"   ✅ Sentiment: {result['sentiment']} {result['emoji']}: PASS")
    print("   ✅ Sentiment tests PASSED\n")

def test_news_fetch():
    print("🧪 Testing News Fetch...")
    agg = NewsAggregator()
    
    async def test():
        news = await agg.get_news()
        return news
    
    articles = asyncio.run(test())
    assert len(articles) > 0, "Should have articles"
    print(f"   ✅ {len(articles)} articles fetched: PASS")
    print("   ✅ News Fetch tests PASSED\n")

def test_message_formatting():
    print("🧪 Testing Message Formatting...")
    agg = NewsAggregator()
    
    async def test():
        articles = await agg.get_news()
        if articles:
            return agg.format_news_message(articles[0])
        return ""
    
    message = asyncio.run(test())
    assert len(message) > 100, "Message should be substantial"
    print(f"   ✅ Formatted message: {len(message)} chars: PASS")
    print("   ✅ Message Formatting tests PASSED\n")

def test_database():
    print("🧪 Testing Database...")
    db = NewsDatabase(db_path="data/test_crypto_news.db")
    db.add_user(999994, "test_user", "telegram")
    user = db.get_user(999994)
    assert user is not None, "User should exist"
    print("   ✅ User creation: PASS")
    print("   ✅ Database tests PASSED\n")

def run_all_tests():
    print("\n" + "="*50)
    print("📰 CRYPTONEWS AI TEST SUITE")
    print("="*50 + "\n")
    try:
        test_news_aggregator()
        test_sentiment()
        test_news_fetch()
        test_message_formatting()
        test_database()
        print("="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        sys.exit(1)

if __name__ == "__main__": run_all_tests()
