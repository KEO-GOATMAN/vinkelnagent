"""
WordPress publisher utility for posting news analysis.
Handles WordPress REST API integration and post formatting.
"""

import logging
import aiohttp
import json
from typing import Optional, Dict, Any
from datetime import datetime

from ..config.settings import settings
from ..models.news_models import ProcessingResult

logger = logging.getLogger(__name__)


class WordPressPublisher:
    """Handles WordPress publishing via REST API."""
    
    def __init__(self):
        """Initialize WordPress publisher."""
        self.base_url = settings.WORDPRESS_URL
        self.username = settings.WORDPRESS_USERNAME
        self.password = settings.WORDPRESS_PASSWORD
        
        # WordPress REST API endpoints
        if self.base_url:
            self.api_base = f"{self.base_url.rstrip('/')}/wp-json/wp/v2"
            self.posts_endpoint = f"{self.api_base}/posts"
    
    async def publish_news_analysis(self, result: ProcessingResult) -> Optional[int]:
        """
        Publish a news analysis result to WordPress.
        
        Args:
            result: The processed news analysis result
            
        Returns:
            WordPress post ID if successful, None otherwise
        """
        if not self._is_configured():
            logger.warning("WordPress not configured, skipping publication")
            return None
        
        try:
            # Generate post content
            post_data = await self._prepare_post_data(result)
            
            # Publish to WordPress
            post_id = await self._create_wordpress_post(post_data)
            
            if post_id:
                logger.info(f"Successfully published news analysis to WordPress. Post ID: {post_id}")
                return post_id
            else:
                logger.error("Failed to publish news analysis to WordPress")
                return None
                
        except Exception as e:
            logger.error(f"Error publishing to WordPress: {e}")
            return None
    
    async def _prepare_post_data(self, result: ProcessingResult) -> Dict[str, Any]:
        """Prepare WordPress post data from processing result."""
        
        # Generate post title
        title = f"Nyhetsanalys: {result.topic}"
        
        # Generate post content with bias summaries and neutral analysis
        content = self._format_post_content(result)
        
        # Generate excerpt
        excerpt = result.neutral_summary.summary[:150] + "..." if len(result.neutral_summary.summary) > 150 else result.neutral_summary.summary
        
        # Generate tags from key facts and topic
        tags = await self._generate_tags(result)
        
        # Prepare post data
        post_data = {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "status": "publish",  # or "draft" for review
            "tags": tags,
            "date": result.processing_timestamp.isoformat(),
            "meta": {
                "news_topic": result.topic,
                "articles_count": len(result.articles_processed),
                "bias_distribution": self._get_bias_distribution(result.articles_processed)
            }
        }
        
        return post_data
    
    def _format_post_content(self, result: ProcessingResult) -> str:
        """Format the complete post content for WordPress."""
        
        content_parts = []
        
        # Add introduction
        content_parts.append(f"<p><strong>Ämne:</strong> {result.topic}</p>")
        content_parts.append(f"<p><em>Analyserade källor: {len(result.articles_processed)} artiklar från svenska medier</em></p>")
        
        # Add bias visualization placeholder (for frontend component)
        if result.bias_visualization_data:
            bias_data_json = json.dumps([
                {
                    "source_name": item.source_name,
                    "bias": item.bias,
                    "url": item.url
                }
                for item in result.bias_visualization_data
            ])
            
            content_parts.append(f'<div class="bias-visualization" data-bias=\'{bias_data_json}\'></div>')
        
        # Add bias-specific summaries
        content_parts.append("<h2>Politiska perspektiv</h2>")
        
        for bias_summary in result.bias_summaries:
            if bias_summary.article_count > 0:
                content_parts.append(f"<h3>{bias_summary.political_bias.title()}-orienterade medier ({bias_summary.article_count} källor)</h3>")
                content_parts.append(f"<p>{bias_summary.summary}</p>")
        
        # Add neutral summary
        content_parts.append("<h2>Neutral sammanfattning</h2>")
        content_parts.append(f"<p>{result.neutral_summary.summary}</p>")
        
        # Add key facts if available
        if result.neutral_summary.key_facts:
            content_parts.append("<h3>Viktiga fakta</h3>")
            content_parts.append("<ul>")
            for fact in result.neutral_summary.key_facts:
                content_parts.append(f"<li>{fact}</li>")
            content_parts.append("</ul>")
        
        # Add internal links if available
        if result.neutral_summary.internal_links:
            content_parts.append("<h3>Relaterade artiklar</h3>")
            content_parts.append("<ul>")
            for link in result.neutral_summary.internal_links:
                content_parts.append(f"<li><a href=\"{link['url']}\">{link['title']}</a></li>")
            content_parts.append("</ul>")
        
        # Add source attribution
        content_parts.append("<h3>Källor</h3>")
        content_parts.append("<ul>")
        for article in result.articles_processed:
            content_parts.append(f"<li><a href=\"{article.url}\" target=\"_blank\">{article.source_name}</a> - {article.title}</li>")
        content_parts.append("</ul>")
        
        # Add timestamp
        timestamp = result.processing_timestamp.strftime("%Y-%m-%d %H:%M")
        content_parts.append(f"<p><em>Analys genomförd: {timestamp} UTC</em></p>")
        
        return "\n".join(content_parts)
    
    async def _generate_tags(self, result: ProcessingResult) -> list:
        """Generate relevant tags for the post."""
        tags = ["nyhetsanalys", "politik", "svenska medier"]
        
        # Add topic-related tags
        topic_words = result.topic.lower().split()
        for word in topic_words:
            if len(word) > 3:  # Only add meaningful words
                tags.append(word)
        
        # Add bias-related tags
        biases_present = [summary.political_bias for summary in result.bias_summaries if summary.article_count > 0]
        if len(biases_present) > 1:
            tags.append("mångfald perspektiv")
        
        return list(set(tags))  # Remove duplicates
    
    def _get_bias_distribution(self, articles) -> Dict[str, int]:
        """Get distribution of articles by political bias."""
        distribution = {}
        for article in articles:
            bias = article.political_bias
            distribution[bias] = distribution.get(bias, 0) + 1
        return distribution
    
    async def _create_wordpress_post(self, post_data: Dict[str, Any]) -> Optional[int]:
        """Create a WordPress post via REST API."""
        
        try:
            # Prepare authentication
            auth = aiohttp.BasicAuth(self.username, self.password)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.posts_endpoint,
                    json=post_data,
                    auth=auth,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 201:  # Created
                        result = await response.json()
                        return result.get("id")
                    else:
                        error_text = await response.text()
                        logger.error(f"WordPress API error: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error creating WordPress post: {e}")
            return None
    
    async def update_post(self, post_id: int, post_data: Dict[str, Any]) -> bool:
        """Update an existing WordPress post."""
        
        if not self._is_configured():
            return False
        
        try:
            auth = aiohttp.BasicAuth(self.username, self.password)
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            update_endpoint = f"{self.posts_endpoint}/{post_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    update_endpoint,
                    json=post_data,
                    auth=auth,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:  # OK
                        logger.info(f"Successfully updated WordPress post {post_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"WordPress update error: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error updating WordPress post: {e}")
            return False
    
    def _is_configured(self) -> bool:
        """Check if WordPress is properly configured."""
        return all([
            self.base_url,
            self.username,
            self.password
        ])


# Global instance
wordpress_publisher = WordPressPublisher() 