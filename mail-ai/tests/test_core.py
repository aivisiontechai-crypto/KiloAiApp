#!/usr/bin/env python3
"""MailAI - Test Suite"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.email_generator import EmailGenerator, EmailDatabase, EMAIL_TYPES, TONES

def test_email_types():
    print("🧪 Testing Email Types...")
    gen = EmailGenerator()
    types = gen.get_email_types()
    assert len(types) == 6, "Should have 6 email types"
    print(f"   ✅ {len(types)} email types: PASS")
    print("   ✅ Email Types tests PASSED\n")

def test_tones():
    print("🧪 Testing Tones...")
    gen = EmailGenerator()
    tones = gen.get_tones()
    assert len(tones) >= 5, "Should have 5+ tones"
    print(f"   ✅ {len(tones)} tones available: PASS")
    print("   ✅ Tones tests PASSED\n")

def test_email_generation():
    print("🧪 Testing Email Generation...")
    gen = EmailGenerator()
    
    async def test_gen():
        result = await gen.generate_email("reply", "Project Update", "Can you send me the report?", "professional", "en")
        return result
    
    result = asyncio.run(test_gen())
    assert result is not None, "Should generate email"
    assert len(result) > 50, "Should have substantial content"
    print(f"   ✅ Generated {len(result)} chars: PASS")
    print("   ✅ Email Generation tests PASSED\n")

def test_database():
    print("🧪 Testing Database...")
    db = EmailDatabase(db_path="data/test_mailai.db")
    db.add_user(999996, "test_user", "telegram")
    user = db.get_user(999996)
    assert user is not None, "User should exist"
    print("   ✅ User creation: PASS")
    print("   ✅ Database tests PASSED\n")

def run_all_tests():
    print("\n" + "="*50)
    print("🧪 MAILAI TEST SUITE")
    print("="*50 + "\n")
    try:
        test_email_types()
        test_tones()
        test_email_generation()
        test_database()
        print("="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        sys.exit(1)

if __name__ == "__main__": run_all_tests()
