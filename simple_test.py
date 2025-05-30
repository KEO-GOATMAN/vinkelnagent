#!/usr/bin/env python3
"""
Simple test script to validate the news agent setup.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables."""
    load_dotenv()
    
    required_vars = [
        'GEMINI_API_KEY',
        'SUPABASE_URL', 
        'SUPABASE_ANON_KEY',
        'SERPER_API_KEY',
        'WORDPRESS_URL',
        'WORDPRESS_USERNAME',
        'WORDPRESS_PASSWORD'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_supabase():
    """Test Supabase connection."""
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        
        client = create_client(url, key)
        
        # Test a simple query
        result = client.table('news_embeddings').select('id').limit(1).execute()
        print("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_gemini():
    """Test Gemini API."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        
        response = model.generate_content("Hello, this is a test.")
        if response.text:
            print("✅ Gemini API connection successful")
            return True
        else:
            print("❌ Gemini API returned no response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running simple setup validation...")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Supabase Database", test_supabase),
        ("Gemini API", test_gemini),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:<20} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Setup is working correctly.")
        print("\nYour news agent is ready to use. You can now:")
        print("1. Test individual components")
        print("2. Deploy to Vercel")
        print("3. Process news articles")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 