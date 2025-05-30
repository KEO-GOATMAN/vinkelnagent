"""
Vercel serverless function for processing news topics.
Handles HTTP POST requests with news topic data and returns analysis results.
"""

import json
import logging
import asyncio
import sys
import os
from typing import Dict, Any

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.news_models import ProcessingInput
from src.agents.news_agent import news_agent

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def handler(request, context):
    """
    Vercel serverless function handler for news topic processing.
    
    Expected POST body:
    {
        "topic_title": "Optional news title",
        "topic_url": "Optional news URL", 
        "topic_description": "Optional description"
    }
    
    Returns:
    {
        "status": "success|error",
        "data": ProcessingResult or error message
    }
    """
    
    # Set CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    try:
        # Handle OPTIONS request for CORS preflight
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Only accept POST requests
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'Method not allowed. Use POST.'
                })
            }
        
        # Parse request body
        try:
            if hasattr(request, 'body'):
                body = json.loads(request.body)
            else:
                # Fallback for different request formats
                body = request.get('body', {})
                if isinstance(body, str):
                    body = json.loads(body)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Invalid JSON in request body: {e}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'Invalid JSON in request body'
                })
            }
        
        # Validate input
        if not any([
            body.get('topic_title'),
            body.get('topic_url'),
            body.get('topic_description')
        ]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'At least one of topic_title, topic_url, or topic_description is required'
                })
            }
        
        # Create processing input
        processing_input = ProcessingInput(
            topic_title=body.get('topic_title'),
            topic_url=body.get('topic_url'),
            topic_description=body.get('topic_description')
        )
        
        logger.info(f"Processing news topic: {processing_input.get_search_query()}")
        
        # Process the news topic asynchronously
        result = asyncio.run(process_news_topic_async(processing_input))
        
        # Convert result to dict for JSON serialization
        result_dict = result.dict() if hasattr(result, 'dict') else result
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'success',
                'data': result_dict
            }, default=str)  # Handle datetime serialization
        }
        
    except Exception as e:
        logger.error(f"Error processing news topic: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            })
        }


async def process_news_topic_async(processing_input: ProcessingInput):
    """Async wrapper for news topic processing."""
    try:
        result = await news_agent.process_news_topic(processing_input)
        return result
    except Exception as e:
        logger.error(f"Error in async processing: {e}")
        raise


# Alternative export for different Vercel configurations
def main(request):
    """Alternative handler name for Vercel compatibility."""
    return handler(request, None)


# For local testing
if __name__ == '__main__':
    # Test the function locally
    import json
    
    class TestRequest:
        def __init__(self, method='POST', body=''):
            self.method = method
            self.body = body
    
    test_body = {
        "topic_title": "Test news topic",
        "topic_description": "Testing the news processing function"
    }
    
    test_request = TestRequest('POST', json.dumps(test_body))
    response = handler(test_request, None)
    print(json.dumps(response, indent=2)) 