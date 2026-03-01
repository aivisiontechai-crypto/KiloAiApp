#!/usr/bin/env python3
"""
LegalAI - Test Suite
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.document_generator import LegalDocumentGenerator, DocumentDatabase


def test_database():
    """Test database operations"""
    print("🧪 Testing Database...")
    
    db = DocumentDatabase(db_path="data/test_legalai.db")
    
    # Test add user
    db.add_user(999998, "test_user", "telegram")
    user = db.get_user(999998)
    
    assert user is not None, "User should exist"
    assert user["username"] == "test_user", "Username should match"
    print("   ✅ User creation: PASS")
    
    print("   ✅ Database tests PASSED\n")


def test_document_generator():
    """Test document generation"""
    print("🧪 Testing Document Generator...")
    
    gen = LegalDocumentGenerator()
    
    # Test available docs
    docs = gen.get_available_docs()
    assert len(docs) > 0, "Should have document types"
    print(f"   ✅ Available docs: {len(docs)} types")
    
    # Test NDA template
    nda = gen.doc_templates.get("nda")
    assert nda is not None, "NDA template should exist"
    assert "variables" in nda, "Should have variables"
    print("   ✅ NDA template: PASS")
    
    # Test document generation (mock)
    async def test_gen():
        result = await gen.generate_document("nda", {
            "disclosing_party": "Acme Corp",
            "receiving_party": "John Smith",
            "effective_date": "2024-01-01",
            "confidential_info": "Trade secrets",
            "duration": "2 years",
            "governing_law": "Delaware"
        })
        return result
    
    result = asyncio.run(test_gen())
    assert result is not None, "Should generate document"
    assert len(result) > 100, "Should have substantial content"
    print("   ✅ Document generation: PASS")
    print(f"   📄 Generated {len(result)} characters")
    
    print("   ✅ Document Generator tests PASSED\n")


def test_pricing():
    """Test pricing structure"""
    print("🧪 Testing Pricing...")
    
    gen = LegalDocumentGenerator()
    
    for doc in gen.get_available_docs():
        assert doc["price"] > 0, f"Price should be set for {doc['id']}"
    
    print(f"   ✅ All {len(gen.get_available_docs())} documents have prices")
    print("   ✅ Pricing tests PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("🧪 LEGALAI TEST SUITE")
    print("="*50 + "\n")
    
    try:
        test_database()
        test_document_generator()
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
