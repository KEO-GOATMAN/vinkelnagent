#!/usr/bin/env python3
"""
Simple test script to validate the news agent setup.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment():
    """Test that all required environment variables are set."""
    logger.info("Testing environment variables...")
    
    required_vars = [
        'GEMINI_API_KEY',
        'SUPABASE_URL', 
        'SUPABASE_ANON_KEY',
        'SERPER_API_KEY',
        'WORDPRESS_URL',
        'WORDPRESS_USERNAME', 
        'WORDPRESS_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        logger.info("✅ All environment variables set")
        return True

def test_supabase():
    """Test Supabase connection."""
    logger.info("Testing Supabase connection...")
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        
        supabase = create_client(url, key)
        
        # Test with correct table name
        result = supabase.table('news_embeddings').select("id").limit(1).execute()
        
        logger.info("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

def test_gemini():
    """Test Gemini API connection."""
    logger.info("Testing Gemini API connection...")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Use the simplest possible API call
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        response = model.generate_content("Hello, please respond with 'API test successful'")
        
        if response and response.text:
            logger.info("✅ Gemini API connection successful")
            return True
        else:
            logger.error("❌ Gemini API returned no response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Gemini API connection failed: {e}")
        return False

async def test_serper():
    """Test Serper API connection."""
    logger.info("Testing Serper API connection...")
    
    try:
        import aiohttp
        
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": os.getenv('SERPER_API_KEY'),
            "Content-Type": "application/json"
        }
        data = {"q": "test query", "num": 1}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    logger.info("✅ Serper API connection successful")
                    return True
                else:
                    logger.error(f"❌ Serper API failed: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Serper API connection failed: {e}")
        return False

async def test_wordpress():
    """Test WordPress connection."""
    logger.info("Testing WordPress connection...")
    
    try:
        import aiohttp
        
        base_url = os.getenv('WORDPRESS_URL')
        username = os.getenv('WORDPRESS_USERNAME')
        password = os.getenv('WORDPRESS_PASSWORD')
        
        api_url = f"{base_url.rstrip('/')}/wp-json/wp/v2/users/me"
        auth = aiohttp.BasicAuth(username, password)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, auth=auth) as response:
                if response.status == 200:
                    logger.info("✅ WordPress connection successful")
                    return True
                else:
                    logger.error(f"❌ WordPress connection failed: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ WordPress connection failed: {e}")
        return False

async def main():
    """Run all tests."""
    logger.info("🧪 Running simplified setup tests...")
    
    results = {}
    
    # Test environment
    results['environment'] = test_environment()
    
    # Test Supabase
    results['supabase'] = test_supabase()
    
    # Test Gemini
    results['gemini'] = test_gemini()
    
    # Test Serper
    results['serper'] = await test_serper()
    
    # Test WordPress
    results['wordpress'] = await test_wordpress()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    all_passed = True
    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{service.capitalize():12} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All tests passed! Ready to deploy!")
    else:
        logger.info("\n⚠️  Some tests failed. Check configuration.")
    
    return all_passed

if __name__ == "__main__":
    load_dotenv()
    
    result = asyncio.run(main())
    exit(0 if result else 1) 