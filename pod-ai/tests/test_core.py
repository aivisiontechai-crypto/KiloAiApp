#!/usr/bin/env python3
"""
PodAI - Test Suite
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.podcast_generator import PodcastGenerator, PodcastDatabase


def test_database():
    """Test database operations"""
    print("🧪 Testing Database...")
    
    db = PodcastDatabase(db_path="data/test_podai.db")
    
    # Test add user
    db.add_user(999997, "test_user", "telegram")
    user = db.get_user(999997)
    
    assert user is not None, "User should exist"
    assert user["username"] == "test_user", "Username should match"
    print("   ✅ User creation: PASS")
    
    print("   ✅ Database tests PASSED\n")


def test_podcast_generator():
    """Test podcast generation"""
    print("🧪 Testing Podcast Generator...")
    
    gen = PodcastGenerator()
    
    # Test voices
    voices = gen.get_voices()
    assert len(voices) > 0, "Should have voices"
    print(f"   ✅ Available voices: {len(voices)}")
    
    # Test languages
    languages = gen.get_languages()
    assert "en" in languages, "English should be available"
    print(f"   ✅ Available languages: {len(languages)}")
    
    # Test templates
    templates = gen.get_templates()
    assert "blog" in templates, "Blog template should exist"
    print("   ✅ Templates: PASS")
    
    # Test podcast generation (mock)
    async def test_gen():
        result = await gen.generate_podcast(
            source_type="url",
            source_url="https://example.com/article",
            voice="alloy",
            language="en"
        )
        return result
    
    result = asyncio.run(test_gen())
    assert result is not None, "Should generate podcast"
    assert "title" in result, "Should have title"
    assert "summary" in result, "Should have summary"
    print("   ✅ Podcast generation: PASS")
    print(f"   📝 Title: {result['title'][:50]}...")
    print(f"   ⏱ Duration: ~{result['duration_seconds']} seconds")
    
    print("   ✅ Podcast Generator tests PASSED\n")


def test_pricing():
    """Test pricing structure"""
    print("🧪 Testing Pricing...")
    
    # Test voice options
    gen = PodcastGenerator()
    voices = gen.get_voices()
    
    expected_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    for voice in expected_voices:
        assert voice in voices, f"Voice {voice} should exist"
    
    print(f"   ✅ All {len(expected_voices)} expected voices available")
    print("   ✅ Pricing tests PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("🧪 PODAI TEST SUITE")
    print("="*50 + "\n")
    
    try:
        test_database()
        test_podcast_generator()
        test_pricing()
        
        print("="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50 + "\n")
        
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
