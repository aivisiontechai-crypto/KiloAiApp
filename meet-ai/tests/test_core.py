#!/usr/bin/env python3
"""
MeetAI - Test Suite
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.meeting_processor import MeetingProcessor, MeetingDatabase


def test_database():
    """Test database operations"""
    print("🧪 Testing Database...")
    
    db = MeetingDatabase()
    
    # Test add user
    db.add_user(999999, "test_user", "telegram")
    user = db.get_user(999999)
    
    assert user is not None, "User should exist"
    assert user["username"] == "test_user", "Username should match"
    print("   ✅ User creation: PASS")
    
    # Test get meetings (empty)
    meetings = db.get_user_meetings(999999)
    assert isinstance(meetings, list), "Meetings should be a list"
    print("   ✅ Get meetings: PASS")
    
    print("   ✅ Database tests PASSED\n")


def test_meeting_processor():
    """Test meeting processor"""
    print("🧪 Testing Meeting Processor...")
    
    processor = MeetingProcessor()
    
    # Test templates
    templates = processor.get_templates()
    assert "standard" in templates, "Standard template should exist"
    assert "action" in templates, "Action template should exist"
    print("   ✅ Get templates: PASS")
    
    # Test meeting processing (mock)
    async def test_async():
        meeting = await processor.process_meeting(
            transcript="This is a test meeting about project updates. John mentioned the deadline is next Friday. Sarah will send the report. We decided to proceed with Option B.",
            title="Test Meeting"
        )
        
        assert meeting is not None, "Meeting should be created"
        assert meeting.summary is not None, "Summary should exist"
        assert meeting.title == "Test Meeting", "Title should match"
        
        return meeting
    
    meeting = asyncio.run(test_async())
    print("   ✅ Process meeting: PASS")
    print(f"   📝 Summary: {meeting.summary[:100]}...")
    print(f"   ✅ Action items: {len(meeting.action_items)} items")
    
    print("   ✅ Meeting Processor tests PASSED\n")


def test_integration():
    """Integration test"""
    print("🧪 Testing Integration...")
    
    db = MeetingDatabase()
    processor = MeetingProcessor()
    
    async def test_full_flow():
        # Create meeting
        meeting = await processor.process_meeting(
            transcript="Test transcript for integration testing. Important decisions were made about the project timeline.",
            title="Integration Test Meeting"
        )
        
        # Save meeting
        db.save_meeting(meeting, 999999)
        
        # Retrieve
        meetings = db.get_user_meetings(999999)
        
        return len(meetings) > 0
    
    result = asyncio.run(test_full_flow())
    assert result, "Meeting should be saved and retrieved"
    print("   ✅ Full integration: PASS")
    
    print("   ✅ Integration tests PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("🧪 MEETAI TEST SUITE")
    print("="*50 + "\n")
    
    try:
        test_database()
        test_meeting_processor()
        test_integration()
        
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
