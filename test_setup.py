#!/usr/bin/env python3
"""
Setup Validation Script for News Agent
Tests API connections and validates configuration before deployment.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any, Optional

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment_variables() -> Dict[str, bool]:
    """Check if all required environment variables are set."""
    required_vars = [
        'GEMINI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'SERPER_API_KEY',
        'WORDPRESS_URL',
        'WORDPRESS_USERNAME',
        'WORDPRESS_PASSWORD'
    ]
    
    results = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        is_set = bool(value and value.strip() and not value.startswith('your_'))
        results[var] = is_set
        
        if not is_set:
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing or invalid environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all variables are properly set.")
    else:
        logger.info("✅ All required environment variables are set")
    
    return results

async def test_supabase_connection() -> bool:
    """Test connection to Supabase."""
    try:
        logger.info("Testing Supabase connection...")
        from src.vectorstores.supabase_store import SupabaseVectorStore
        
        store = SupabaseVectorStore()
        
        # Try a simple query to test connection
        try:
            result = store.client.table('news_embeddings').select("id").limit(1).execute()
            logger.info("✅ Supabase connection successful")
            return True
        except Exception as e:
            if "relation \"news_embeddings\" does not exist" in str(e):
                logger.warning("⚠️  Supabase connected but 'news_embeddings' table not found")
                logger.warning("   Run the setup script: setup/supabase_setup.sql")
                return False
            else:
                raise e
            
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

async def test_gemini_api() -> bool:
    """Test Google Gemini API connection."""
    try:
        logger.info("Testing Google Gemini API...")
        from src.components.llm_manager import LLMManager
        
        llm_manager = LLMManager()
        
        # Test with a simple prompt
        test_messages = [
            {"role": "user", "content": "Hello, this is a test. Please respond with 'API test successful'."}
        ]
        
        response = await llm_manager.llm.ainvoke("Hello, this is a test. Please respond with 'API test successful'.")
        
        if response and hasattr(response, 'content'):
            logger.info("✅ Gemini API connection successful")
            return True
        else:
            logger.error("❌ Gemini API returned unexpected response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Gemini API connection failed: {e}")
        return False

async def test_serper_api() -> bool:
    """Test Serper API connection."""
    try:
        logger.info("Testing Serper API...")
        from src.utils.web_scraper import WebScraper
        
        scraper = WebScraper()
        
        # Test search with simple query
        results = await scraper.search_web_for_topic("test query", max_results=1)
        
        if results:
            logger.info("✅ Serper API connection successful")
            return True
        else:
            logger.warning("⚠️  Serper API connected but returned no results")
            return True  # Still consider this a success
            
    except Exception as e:
        logger.error(f"❌ Serper API connection failed: {e}")
        return False

async def test_wordpress_connection() -> bool:
    """Test WordPress API connection."""
    try:
        logger.info("Testing WordPress connection...")
        from src.utils.wordpress_publisher import WordPressPublisher
        
        publisher = WordPressPublisher()
        
        # Test authentication by trying to get user info
        is_connected = await publisher.test_connection()
        
        if is_connected:
            logger.info("✅ WordPress connection successful")
            return True
        else:
            logger.error("❌ WordPress authentication failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ WordPress connection failed: {e}")
        return False

def test_dependencies() -> bool:
    """Test if all required Python dependencies are installed."""
    logger.info("Testing Python dependencies...")
    
    required_modules = [
        'langchain',
        'langchain_google_genai',
        'sentence_transformers',
        'supabase',
        'requests',
        'bs4',  # beautifulsoup4 imports as bs4
        'newspaper',  # newspaper3k imports as newspaper
        'feedparser',
        'pydantic'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        logger.error("Install with: pip install -r requirements.txt")
        return False
    else:
        logger.info("✅ All dependencies are installed")
        return True

async def run_full_test():
    """Run all tests and provide a summary."""
    logger.info("🚀 Starting News Agent setup validation...")
    logger.info("=" * 50)
    
    # Test dependencies first
    deps_ok = test_dependencies()
    if not deps_ok:
        logger.error("❌ Dependency test failed. Please install requirements first.")
        return False
    
    # Test environment variables
    env_results = check_environment_variables()
    env_ok = all(env_results.values())
    
    if not env_ok:
        logger.error("❌ Environment validation failed. Please fix your .env file.")
        return False
    
    # Test API connections
    logger.info("\nTesting API connections...")
    
    test_results = {}
    
    test_results['supabase'] = await test_supabase_connection()
    test_results['gemini'] = await test_gemini_api()
    test_results['serper'] = await test_serper_api()
    test_results['wordpress'] = await test_wordpress_connection()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 50)
    
    all_passed = True
    
    for service, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{service.capitalize():12} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All tests passed! Your setup is ready for deployment.")
        logger.info("\nNext steps:")
        logger.info("1. Run setup/supabase_setup.sql in your Supabase SQL editor")
        logger.info("2. Deploy to Vercel: vercel --prod")
        logger.info("3. Test with: curl -X POST [your-url]/api/process_news_topic")
    else:
        logger.info("\n⚠️  Some tests failed. Please fix the issues above before deploying.")
    
    return all_passed

def main():
    """Main function to run the setup validation."""
    try:
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Run async tests
        result = asyncio.run(run_full_test())
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 