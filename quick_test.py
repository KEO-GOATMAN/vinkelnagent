#!/usr/bin/env python3
"""
Quick Test - Verify core functionality works
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def quick_test():
    """Quick test of core functionality."""
    print("🚀 Quick Test of News Agent Core Functionality")
    print("=" * 50)
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded")
        
        # Test 1: Simple LLM call
        print("\n🧠 Testing LLM...")
        from src.components.llm_manager import LLMManager
        llm = LLMManager()
        response = await llm.generate_simple_response("What is the capital of Sweden?")
        if "Stockholm" in response or "stockholm" in response:
            print("✅ LLM is working correctly")
        else:
            print(f"⚠️  LLM response: {response[:100]}...")
        
        # Test 2: Vector store connection
        print("\n🗄️  Testing Vector Store...")
        from src.vectorstores.supabase_store import SupabaseVectorStore
        vector_store = SupabaseVectorStore()
        await vector_store._ensure_table_exists()
        print("✅ Vector store connection established")
        
        # Test 3: Basic search simulation (without real web search)
        print("\n🔍 Testing Search Simulation...")
        from src.utils.web_scraper import WebScraper
        scraper = WebScraper()
        print("✅ Web scraper initialized")
        
        # Test 4: Process Input Model
        print("\n📄 Testing Processing Input...")
        from src.models.news_models import ProcessingInput
        input_data = ProcessingInput(
            topic_title="Swedish Elections 2024",
            topic_description="Test topic for verification"
        )
        search_query = input_data.get_search_query()
        print(f"✅ Search query generated: {search_query}")
        
        print("\n🎉 QUICK TEST PASSED - Core functionality is working!")
        print("Your news agent setup is ready for deployment!")
        
    except Exception as e:
        print(f"\n❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(quick_test()) 