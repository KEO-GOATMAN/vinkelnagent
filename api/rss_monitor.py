#!/usr/bin/env python3
"""
RSS Monitor API Endpoint
========================

Vercel serverless function for automated RSS feed monitoring.
Triggered hourly by Vercel Cron Job.
"""

import asyncio
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler
import json
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for RSS monitoring"""
        try:
            # Run RSS monitoring
            result = asyncio.run(self.monitor_rss_feeds())
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'RSS monitoring completed',
                'articles_processed': result.get('articles_processed', 0),
                'new_articles': result.get('new_articles', 0)
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"RSS monitoring error: {e}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e)
            }
            
            self.wfile.write(json.dumps(error_response).encode())
    
    async def monitor_rss_feeds(self):
        """Monitor RSS feeds for new articles"""
        try:
            from utils.rss_parser import RSSParser
            from components.vector_store import SupabaseVectorStore
            from agents.news_agent import NewsAgent
            
            logger.info("Starting RSS feed monitoring...")
            
            # Initialize components
            rss_parser = RSSParser()
            vector_store = SupabaseVectorStore()
            news_agent = NewsAgent()
            
            # Get recent articles from RSS feeds
            articles = await rss_parser.get_recent_articles(hours=1)
            
            logger.info(f"Found {len(articles)} recent articles")
            
            new_articles = 0
            
            # Process each article
            for article in articles:
                try:
                    # Check if article already exists in vector store
                    existing = await vector_store.search_by_url(article.url)
                    
                    if not existing:
                        # Process new article
                        await news_agent.process_single_article(article)
                        new_articles += 1
                        logger.info(f"Processed new article: {article.title}")
                    
                except Exception as e:
                    logger.error(f"Error processing article {article.url}: {e}")
                    continue
            
            logger.info(f"RSS monitoring complete. Processed {new_articles} new articles.")
            
            return {
                'articles_processed': len(articles),
                'new_articles': new_articles
            }
            
        except Exception as e:
            logger.error(f"RSS monitoring failed: {e}")
            raise

# For local testing
if __name__ == "__main__":
    import unittest.mock
    
    class MockRequest:
        def __init__(self):
            self.method = 'GET'
    
    mock_handler = handler(MockRequest(), ('127.0.0.1', 8000), None)
    mock_handler.do_GET() 