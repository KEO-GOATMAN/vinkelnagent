#!/usr/bin/env python3
"""
Real Workflow Test for News Agent
Tests the complete end-to-end functionality of the politically-aware news agent.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our components
from src.models.news_models import ProcessingInput
from src.agents.news_agent import NewsAgent
from src.config.settings import settings

class RealWorkflowTest:
    """Real workflow test class that exercises the complete system."""
    
    def __init__(self):
        self.news_agent = NewsAgent()
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': []
        }
    
    async def run_all_tests(self):
        """Run all real workflow tests."""
        print("🚀 Starting Real Workflow Tests for News Agent")
        print("=" * 60)
        
        # Test 1: Simple topic processing
        await self.test_simple_topic_processing()
        
        # Test 2: URL-based processing
        await self.test_url_based_processing()
        
        # Test 3: Complex topic with description
        await self.test_complex_topic_processing()
        
        # Test 4: API endpoint simulation
        await self.test_api_endpoint_simulation()
        
        # Print final results
        self.print_final_results()
    
    async def test_simple_topic_processing(self):
        """Test processing a simple news topic."""
        print("\n📰 Test 1: Simple Topic Processing")
        print("-" * 40)
        
        try:
            self.test_results['tests_run'] += 1
            
            # Create processing input
            input_data = ProcessingInput(
                topic_title="Swedish Elections 2024",
                topic_description="Latest news about Swedish political elections"
            )
            
            print(f"🔍 Processing topic: {input_data.get_search_query()}")
            
            # Process the topic
            result = await self.news_agent.process_news_topic(input_data)
            
            # Validate result
            if self._validate_processing_result(result, "simple_topic"):
                print("✅ Simple topic processing: PASSED")
                self.test_results['tests_passed'] += 1
            else:
                print("❌ Simple topic processing: FAILED")
                self.test_results['tests_failed'] += 1
                
        except Exception as e:
            print(f"❌ Simple topic processing: FAILED with exception: {e}")
            self.test_results['tests_failed'] += 1
            self.test_results['failures'].append(f"Simple topic: {str(e)}")
    
    async def test_url_based_processing(self):
        """Test processing with a specific news URL."""
        print("\n🔗 Test 2: URL-Based Processing")
        print("-" * 40)
        
        try:
            self.test_results['tests_run'] += 1
            
            # Create processing input with URL
            input_data = ProcessingInput(
                topic_url="https://www.aftonbladet.se/nyheter/a/dummy-article",
                topic_description="Test article processing from URL"
            )
            
            print(f"🔍 Processing URL: {input_data.topic_url}")
            
            # Process the topic
            result = await self.news_agent.process_news_topic(input_data)
            
            # Validate result
            if self._validate_processing_result(result, "url_based"):
                print("✅ URL-based processing: PASSED")
                self.test_results['tests_passed'] += 1
            else:
                print("❌ URL-based processing: FAILED")
                self.test_results['tests_failed'] += 1
                
        except Exception as e:
            print(f"❌ URL-based processing: FAILED with exception: {e}")
            self.test_results['tests_failed'] += 1
            self.test_results['failures'].append(f"URL-based: {str(e)}")
    
    async def test_complex_topic_processing(self):
        """Test processing a complex topic with multiple input types."""
        print("\n🧠 Test 3: Complex Topic Processing")
        print("-" * 40)
        
        try:
            self.test_results['tests_run'] += 1
            
            # Create complex processing input
            input_data = ProcessingInput(
                topic_title="Swedish Climate Policy Changes",
                topic_url="https://www.dn.se/dummy-climate-article",
                topic_description="Recent changes to Swedish environmental policies and their political implications"
            )
            
            print(f"🔍 Processing complex topic: {input_data.get_search_query()}")
            
            # Process the topic
            result = await self.news_agent.process_news_topic(input_data)
            
            # Validate result with enhanced checks
            if self._validate_processing_result(result, "complex_topic", enhanced=True):
                print("✅ Complex topic processing: PASSED")
                self.test_results['tests_passed'] += 1
            else:
                print("❌ Complex topic processing: FAILED")
                self.test_results['tests_failed'] += 1
                
        except Exception as e:
            print(f"❌ Complex topic processing: FAILED with exception: {e}")
            self.test_results['tests_failed'] += 1
            self.test_results['failures'].append(f"Complex topic: {str(e)}")
    
    async def test_api_endpoint_simulation(self):
        """Test the API endpoint by simulating HTTP requests."""
        print("\n🌐 Test 4: API Endpoint Simulation")
        print("-" * 40)
        
        try:
            self.test_results['tests_run'] += 1
            
            # Import the API handler
            sys.path.append('api')
            from api.process_news_topic import handler
            
            # Create mock request
            class MockRequest:
                def __init__(self, method='POST', body=''):
                    self.method = method
                    self.body = body
            
            # Test data
            test_body = {
                "topic_title": "Swedish Healthcare Reform",
                "topic_description": "New healthcare policies being debated in Swedish parliament"
            }
            
            request = MockRequest('POST', json.dumps(test_body))
            
            print(f"🔍 Simulating API call with: {test_body['topic_title']}")
            
            # Call the API handler
            response = handler(request, None)
            
            # Validate API response
            if self._validate_api_response(response):
                print("✅ API endpoint simulation: PASSED")
                self.test_results['tests_passed'] += 1
            else:
                print("❌ API endpoint simulation: FAILED")
                self.test_results['tests_failed'] += 1
                
        except Exception as e:
            print(f"❌ API endpoint simulation: FAILED with exception: {e}")
            self.test_results['tests_failed'] += 1
            self.test_results['failures'].append(f"API endpoint: {str(e)}")
    
    def _validate_processing_result(self, result, test_type: str, enhanced: bool = False) -> bool:
        """Validate a processing result."""
        try:
            if not result:
                print(f"  ❌ No result returned for {test_type}")
                return False
            
            # Check if it's an error result
            if hasattr(result, 'error') and result.error:
                print(f"  ❌ Error in result: {result.error}")
                return False
            
            # Basic validations
            validations = [
                (hasattr(result, 'topic'), "Has topic"),
                (hasattr(result, 'neutral_summary'), "Has neutral summary"),
                (hasattr(result, 'bias_summaries'), "Has bias summaries"),
                (hasattr(result, 'processing_timestamp'), "Has timestamp"),
            ]
            
            if enhanced:
                validations.extend([
                    (hasattr(result, 'bias_visualization_data'), "Has visualization data"),
                    (hasattr(result, 'articles_processed'), "Has processed articles"),
                ])
            
            passed_validations = 0
            for check, description in validations:
                if check:
                    print(f"    ✅ {description}")
                    passed_validations += 1
                else:
                    print(f"    ❌ {description}")
            
            # Additional content checks
            if hasattr(result, 'neutral_summary') and result.neutral_summary:
                if hasattr(result.neutral_summary, 'summary') and result.neutral_summary.summary:
                    print(f"    ✅ Neutral summary content: {len(result.neutral_summary.summary)} chars")
                    passed_validations += 1
                else:
                    print(f"    ❌ Empty neutral summary content")
            
            if hasattr(result, 'bias_summaries') and result.bias_summaries:
                bias_count = len([s for s in result.bias_summaries if s.article_count > 0])
                print(f"    ✅ Active bias summaries: {bias_count}")
                passed_validations += 1
            
            # Consider test passed if most validations pass
            required_passes = len(validations) + 1 if enhanced else len(validations)
            success_rate = passed_validations / (required_passes + 1)
            
            return success_rate >= 0.7  # 70% success rate required
            
        except Exception as e:
            print(f"  ❌ Validation error: {e}")
            return False
    
    def _validate_api_response(self, response) -> bool:
        """Validate an API response."""
        try:
            if not response:
                print("    ❌ No API response")
                return False
            
            # Check status code
            if response.get('statusCode') != 200:
                print(f"    ❌ Bad status code: {response.get('statusCode')}")
                return False
            
            # Check response structure
            body = response.get('body')
            if not body:
                print("    ❌ No response body")
                return False
            
            # Parse JSON body
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print("    ❌ Invalid JSON in response body")
                return False
            
            # Check response format
            if data.get('status') != 'success':
                print(f"    ❌ Response status not success: {data.get('status')}")
                print(f"    ❌ Error message: {data.get('message', 'Unknown error')}")
                return False
            
            if 'data' not in data:
                print("    ❌ No data in response")
                return False
            
            print("    ✅ Valid API response structure")
            print(f"    ✅ Response size: {len(body)} chars")
            
            return True
            
        except Exception as e:
            print(f"    ❌ API validation error: {e}")
            return False
    
    def print_final_results(self):
        """Print final test results."""
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 60)
        
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")
        
        if self.test_results['tests_failed'] > 0:
            print("\n❌ FAILURES:")
            for failure in self.test_results['failures']:
                print(f"  - {failure}")
        
        success_rate = (self.test_results['tests_passed'] / self.test_results['tests_run']) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print("🎉 OVERALL RESULT: PASSED")
        else:
            print("💥 OVERALL RESULT: FAILED")

async def main():
    """Main function to run the real workflow tests."""
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check critical environment variables
        required_vars = ['GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return
        
        # Run tests
        test_runner = RealWorkflowTest()
        await test_runner.run_all_tests()
        
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main()) 