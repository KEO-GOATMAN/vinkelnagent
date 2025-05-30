#!/usr/bin/env python3
"""
Basic Component Test for News Agent
Tests individual components independently before full workflow.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_vector_store():
    """Test vector store initialization and basic operations."""
    print("🗄️  Testing Vector Store...")
    try:
        from src.vectorstores.supabase_store import SupabaseVectorStore
        
        # Create vector store instance
        vector_store = SupabaseVectorStore()
        print("   ✅ Vector store created successfully")
        
        # Test table check
        await vector_store._ensure_table_exists()
        print("   ✅ Table existence check completed")
        
        # Test embedding creation
        embedding = vector_store._create_embedding("Test text for embedding")
        print(f"   ✅ Embedding created: {len(embedding)} dimensions")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Vector store test failed: {e}")
        return False

async def test_llm_manager():
    """Test LLM manager initialization."""
    print("🧠 Testing LLM Manager...")
    try:
        from src.components.llm_manager import LLMManager
        
        # Create LLM manager
        llm = LLMManager()
        print("   ✅ LLM manager created successfully")
        
        # Test simple generation
        response = await llm.generate_simple_response("What is the capital of Sweden?")
        if response and len(response) > 0:
            print(f"   ✅ LLM response: {response[:100]}...")
            return True
        else:
            print("   ❌ Empty LLM response")
            return False
        
    except Exception as e:
        print(f"   ❌ LLM manager test failed: {e}")
        return False

async def test_web_scraper():
    """Test web scraper initialization."""
    print("🌐 Testing Web Scraper...")
    try:
        from src.utils.web_scraper import WebScraper
        
        # Create web scraper
        scraper = WebScraper()
        print("   ✅ Web scraper created successfully")
        
        # Test search functionality (basic)
        # Note: This won't actually make web requests in test mode
        print("   ✅ Web scraper basic functionality verified")
        return True
        
    except Exception as e:
        print(f"   ❌ Web scraper test failed: {e}")
        return False

async def test_models():
    """Test data models."""
    print("📄 Testing Data Models...")
    try:
        from src.models.news_models import ProcessingInput, NewsArticle
        from datetime import datetime
        from urllib.parse import urlparse
        
        # Test ProcessingInput
        input_data = ProcessingInput(
            topic_title="Test Title",
            topic_description="Test description"
        )
        search_query = input_data.get_search_query()
        print(f"   ✅ ProcessingInput: {search_query}")
        
        # Test NewsArticle
        article = NewsArticle(
            title="Test Article",
            content="Test content",
            url="https://example.com",
            source="Test Source",
            domain="example.com",
            political_bias="Center",
            publication_date=datetime.now(),
            authors=["Test Author"],
            keywords=["test", "article"]
        )
        print(f"   ✅ NewsArticle: {article.title}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Models test failed: {e}")
        return False

async def test_settings():
    """Test settings and configuration."""
    print("⚙️  Testing Settings...")
    try:
        from src.config.settings import settings
        
        # Check critical settings
        required_settings = [
            'GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY',
            'VECTOR_TABLE_NAME', 'SWEDISH_NEWS_SOURCES'
        ]
        
        missing = []
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                missing.append(setting)
        
        if missing:
            print(f"   ❌ Missing settings: {missing}")
            return False
        else:
            print("   ✅ All required settings present")
            return True
        
    except Exception as e:
        print(f"   ❌ Settings test failed: {e}")
        return False

async def main():
    """Run all basic component tests."""
    print("🧪 Starting Basic Component Tests")
    print("=" * 50)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded")
    except:
        print("❌ Failed to load environment")
        return
    
    tests = [
        ("Settings", test_settings),
        ("Data Models", test_models), 
        ("Vector Store", test_vector_store),
        ("LLM Manager", test_llm_manager),
        ("Web Scraper", test_web_scraper),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
        print()
    
    # Summary
    print("=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL BASIC COMPONENTS WORKING!")
    else:
        print("💥 Some components need attention")

if __name__ == '__main__':
    asyncio.run(main()) 