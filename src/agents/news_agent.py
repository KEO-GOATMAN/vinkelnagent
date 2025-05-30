"""
Main News Agent that orchestrates the entire news processing workflow.
Handles topic processing, bias analysis, RAG enhancement, and WordPress publishing.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..config.settings import settings
from ..models.news_models import (
    ProcessingInput, ProcessingResult, NewsArticle,
    BiasSpecificSummary, NeutralSummary, BiasVisualizationData
)
from ..utils.web_scraper import web_scraper
from ..vectorstores.supabase_store import vector_store
from ..components.llm_manager import llm_manager
from ..utils.wordpress_publisher import wordpress_publisher

logger = logging.getLogger(__name__)


class NewsAgent:
    """Main agent that orchestrates the news processing workflow."""
    
    def __init__(self):
        """Initialize the news agent."""
        self.web_scraper = web_scraper
        self.vector_store = vector_store
        self.llm_manager = llm_manager
        self.wordpress_publisher = wordpress_publisher
    
    async def process_news_topic(self, input_data: ProcessingInput) -> ProcessingResult:
        """
        Process a news topic through the complete workflow:
        1. Find relevant articles
        2. Generate bias-specific summaries
        3. Create neutral summary with RAG enhancement
        4. Prepare visualization data
        5. Store articles in vector database
        6. Publish to WordPress
        """
        try:
            logger.info(f"Starting news processing for topic: {input_data.get_search_query()}")
            
            # Step 1: Source Discovery & Content Retrieval
            articles = await self._discover_and_extract_articles(input_data)
            
            if not articles:
                logger.warning("No articles found for the given topic")
                return self._create_error_result("No articles found for the given topic")
            
            logger.info(f"Found {len(articles)} articles across {len(set(a.political_bias for a in articles))} bias categories")
            
            # Step 2: Retrieve related context from vector database (RAG)
            related_context = await self._retrieve_related_context(input_data.get_search_query())
            
            # Step 3: Generate bias-specific summaries
            bias_summaries = await self._generate_bias_summaries(articles)
            
            # Step 4: Generate neutral summary with RAG enhancement
            neutral_summary = await self._generate_neutral_summary(
                articles, related_context, input_data.get_search_query()
            )
            
            # Step 5: Prepare bias visualization data
            bias_visualization_data = await self._generate_bias_visualization_data(articles)
            
            # Step 6: Store articles in vector database
            await self._store_articles_in_vector_db(articles)
            
            # Step 7: Create processing result
            result = ProcessingResult(
                topic=input_data.get_search_query(),
                neutral_summary=neutral_summary,
                bias_summaries=bias_summaries,
                bias_visualization_data=bias_visualization_data,
                articles_processed=articles,
                processing_timestamp=datetime.utcnow()
            )
            
            # Step 8: Publish to WordPress
            wordpress_post_id = await self._publish_to_wordpress(result)
            if wordpress_post_id:
                result.wordpress_post_id = wordpress_post_id
            
            logger.info(f"Successfully processed news topic: {input_data.get_search_query()}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing news topic: {e}")
            return self._create_error_result(f"Processing error: {str(e)}")
    
    async def _discover_and_extract_articles(self, input_data: ProcessingInput) -> List[NewsArticle]:
        """Discover and extract articles for the given topic."""
        try:
            search_query = input_data.get_search_query()
            
            # Use web scraper to find articles
            articles = await self.web_scraper.find_articles_for_topic(search_query)
            
            # If we have a specific URL in input, try to extract that article too
            if input_data.topic_url:
                from urllib.parse import urlparse
                from ..config.settings import SWEDISH_NEWS_SOURCES
                
                domain = urlparse(str(input_data.topic_url)).netloc.lower()
                
                # Find matching source info
                source_info = None
                for source_domain, info in SWEDISH_NEWS_SOURCES.items():
                    if source_domain in domain or domain in source_domain:
                        source_info = info
                        break
                
                if source_info:
                    additional_article = await self.web_scraper.extract_article_content(
                        str(input_data.topic_url), source_info
                    )
                    if additional_article and additional_article not in articles:
                        articles.append(additional_article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error discovering articles: {e}")
            return []
    
    async def _retrieve_related_context(self, topic: str) -> List:
        """Retrieve related articles from vector database for RAG enhancement."""
        try:
            related_entries = await self.vector_store.similarity_search(
                topic, limit=5, similarity_threshold=0.7
            )
            
            # Extract just the entries (not similarity scores)
            context_entries = [entry for entry, score in related_entries]
            
            logger.info(f"Retrieved {len(context_entries)} related articles for context")
            return context_entries
            
        except Exception as e:
            logger.error(f"Error retrieving related context: {e}")
            return []
    
    async def _generate_bias_summaries(self, articles: List[NewsArticle]) -> List[BiasSpecificSummary]:
        """Generate bias-specific summaries for all political leanings."""
        try:
            bias_summaries = await self.llm_manager.process_all_bias_summaries(articles)
            
            # Filter out summaries with no articles
            valid_summaries = [summary for summary in bias_summaries if summary.article_count > 0]
            
            logger.info(f"Generated {len(valid_summaries)} valid bias summaries")
            return bias_summaries  # Return all, including empty ones for completeness
            
        except Exception as e:
            logger.error(f"Error generating bias summaries: {e}")
            return []
    
    async def _generate_neutral_summary(
        self, 
        articles: List[NewsArticle], 
        related_context: List, 
        topic: str
    ) -> NeutralSummary:
        """Generate neutral summary enhanced by RAG context."""
        try:
            neutral_summary = await self.llm_manager.generate_neutral_summary(
                articles, related_context, topic
            )
            
            logger.info("Generated neutral summary with RAG enhancement")
            return neutral_summary
            
        except Exception as e:
            logger.error(f"Error generating neutral summary: {e}")
            return NeutralSummary(
                summary=f"Error generating neutral summary: {str(e)}",
                key_facts=[],
                related_context=[],
                internal_links=[]
            )
    
    async def _generate_bias_visualization_data(
        self, 
        articles: List[NewsArticle]
    ) -> List[BiasVisualizationData]:
        """Generate data for bias visualization component."""
        try:
            visualization_data = await self.llm_manager.generate_bias_visualization_data(articles)
            
            logger.info(f"Generated bias visualization data for {len(articles)} articles")
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error generating bias visualization data: {e}")
            return []
    
    async def _store_articles_in_vector_db(self, articles: List[NewsArticle]) -> None:
        """Store processed articles in vector database for future RAG retrieval."""
        try:
            await self.vector_store.add_articles_batch(articles)
            
            logger.info(f"Stored {len(articles)} articles in vector database")
            
        except Exception as e:
            logger.error(f"Error storing articles in vector database: {e}")
    
    async def _publish_to_wordpress(self, result: ProcessingResult) -> Optional[int]:
        """Publish the processing result to WordPress."""
        try:
            if not settings.WORDPRESS_URL:
                logger.warning("WordPress URL not configured, skipping publication")
                return None
            
            post_id = await self.wordpress_publisher.publish_news_analysis(result)
            
            if post_id:
                logger.info(f"Published article to WordPress with post ID: {post_id}")
            else:
                logger.warning("Failed to publish to WordPress")
            
            return post_id
            
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            return None
    
    def _create_error_result(self, error_message: str) -> ProcessingResult:
        """Create a processing result for error cases."""
        return ProcessingResult(
            topic="Error",
            neutral_summary=NeutralSummary(
                summary=error_message,
                key_facts=[],
                related_context=[],
                internal_links=[]
            ),
            bias_summaries=[],
            bias_visualization_data=[],
            articles_processed=[],
            processing_timestamp=datetime.utcnow(),
            wordpress_post_id=None
        )
    
    async def process_rss_feeds(self) -> Dict[str, Any]:
        """
        Process recent RSS feeds for new articles.
        This is called by the Vercel cron job.
        """
        try:
            logger.info("Starting RSS feed processing")
            
            # Get recent RSS articles
            recent_items = await self.web_scraper.get_recent_rss_articles(hours=6)
            
            if not recent_items:
                logger.info("No recent RSS items found")
                return {"status": "success", "items_processed": 0}
            
            # Group items by topic/keyword (simplified approach)
            # In a real implementation, you might use clustering or topic modeling
            processed_count = 0
            
            for item in recent_items[:10]:  # Limit to 10 items per run
                try:
                    # Try to extract the full article
                    from ..config.settings import SWEDISH_NEWS_SOURCES
                    from urllib.parse import urlparse
                    
                    domain = urlparse(str(item.link)).netloc.lower()
                    source_info = None
                    
                    for source_domain, info in SWEDISH_NEWS_SOURCES.items():
                        if source_domain in domain or domain in source_domain:
                            source_info = info
                            break
                    
                    if source_info:
                        article = await self.web_scraper.extract_article_content(
                            str(item.link), source_info
                        )
                        
                        if article:
                            # Store in vector database for future retrieval
                            await self.vector_store.add_article(article)
                            processed_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing RSS item {item.link}: {e}")
                    continue
            
            logger.info(f"RSS processing completed. Processed {processed_count} articles")
            return {
                "status": "success", 
                "items_found": len(recent_items),
                "items_processed": processed_count
            }
            
        except Exception as e:
            logger.error(f"Error processing RSS feeds: {e}")
            return {"status": "error", "error": str(e)}


# Global instance
news_agent = NewsAgent() 