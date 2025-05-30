"""
Vercel cron job function for processing RSS feeds.
Runs on a schedule to monitor new articles and populate the vector database.
"""

import json
import logging
import asyncio
import sys
import os
from typing import Dict, Any

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agents.news_agent import news_agent

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def handler(request, context):
    """
    Vercel cron job handler for RSS feed processing.
    
    This function is triggered by Vercel cron jobs (configured in vercel.json)
    to periodically check RSS feeds for new articles and process them into
    the vector database for future RAG enhancement.
    
    Returns:
    {
        "status": "success|error",
        "data": {
            "items_found": int,
            "items_processed": int,
            "processing_time": float
        }
    }
    """
    
    import time
    start_time = time.time()
    
    # Set response headers
    headers = {
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("Starting RSS feed processing cron job")
        
        # Process RSS feeds asynchronously
        result = asyncio.run(process_rss_feeds_async())
        
        processing_time = time.time() - start_time
        result['processing_time'] = round(processing_time, 2)
        
        logger.info(f"RSS processing completed in {processing_time:.2f}s: {result}")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'success',
                'data': result
            })
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error in RSS processing cron job: {e}")
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': f'RSS processing error: {str(e)}',
                'processing_time': round(processing_time, 2)
            })
        }


async def process_rss_feeds_async() -> Dict[str, Any]:
    """Async wrapper for RSS feed processing."""
    try:
        result = await news_agent.process_rss_feeds()
        return result
    except Exception as e:
        logger.error(f"Error in async RSS processing: {e}")
        raise


def health_check(request, context):
    """
    Health check endpoint for the RSS processing system.
    Can be used to verify that the cron job is working correctly.
    """
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": asyncio.run(get_current_timestamp()),
            "version": "1.0.0",
            "components": {}
        }
        
        # Check if we can import required modules
        try:
            from src.agents.news_agent import news_agent
            health_status["components"]["news_agent"] = "ok"
        except Exception as e:
            health_status["components"]["news_agent"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check if environment variables are set
        try:
            from src.config.settings import settings
            if settings.GOOGLE_API_KEY:
                health_status["components"]["google_api"] = "configured"
            else:
                health_status["components"]["google_api"] = "not_configured"
                health_status["status"] = "degraded"
                
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                health_status["components"]["supabase"] = "configured"
            else:
                health_status["components"]["supabase"] = "not_configured"
                health_status["status"] = "degraded"
                
        except Exception as e:
            health_status["components"]["config"] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        status_code = 200 if health_status["status"] == "healthy" else 500
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(health_status, default=str)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "unhealthy",
                "error": str(e)
            })
        }


async def get_current_timestamp():
    """Get current timestamp for health check."""
    from datetime import datetime
    return datetime.utcnow().isoformat()


# Alternative export for different Vercel configurations
def main(request):
    """Alternative handler name for Vercel compatibility."""
    return handler(request, None)


# For local testing
if __name__ == '__main__':
    # Test the RSS processing function locally
    import json
    
    class TestRequest:
        def __init__(self, method='GET'):
            self.method = method
    
    print("Testing RSS processing function...")
    test_request = TestRequest('GET')
    response = handler(test_request, None)
    print(json.dumps(response, indent=2))
    
    print("\nTesting health check...")
    health_response = health_check(test_request, None)
    print(json.dumps(health_response, indent=2)) 