"""
Web scraping and content extraction utilities for Swedish news sources.
Handles RSS feeds, article extraction, and web search integration.
"""

import asyncio
import aiohttp
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import trafilatura
import logging

from ..config.settings import settings, get_all_rss_feeds
from ..models.news_models import NewsArticle, RSSFeedItem, SearchResult

logger = logging.getLogger(__name__)


class WebScraper:
    """Handles web scraping and content extraction for news sources."""
    
    def __init__(self):
        """Initialize the web scraper with session configuration."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    async def extract_article_content(self, url: str, source_info: Dict) -> Optional[NewsArticle]:
        """Extract article content from a URL."""
        try:
            # Download the webpage
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract content using trafilatura (more reliable for news sites)
            content = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=False,
                favor_precision=True
            )
            
            if not content:
                logger.warning(f"Could not extract content from {url}")
                return None
            
            # Fallback to BeautifulSoup for title extraction
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find title
            title = ""
            title_selectors = ['h1', 'title', '[property="og:title"]', '.article-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            if not title:
                title = url  # Fallback to URL
            
            # Try to extract publication date
            pub_date = None
            date_selectors = [
                '[property="article:published_time"]',
                '[name="publish-date"]',
                '.publish-date',
                '.article-date'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_str = date_elem.get('content') or date_elem.get_text()
                    try:
                        pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        break
                    except:
                        continue
            
            # Try to extract authors
            authors = []
            author_selectors = [
                '[rel="author"]',
                '[name="author"]',
                '.author',
                '.byline'
            ]
            
            for selector in author_selectors:
                author_elems = soup.select(selector)
                for elem in author_elems:
                    author = elem.get_text().strip()
                    if author and author not in authors:
                        authors.append(author)
            
            # Create NewsArticle object
            article = NewsArticle(
                title=title,
                content=content,
                url=url,
                source=source_info['name'],
                domain=source_info.get('search_domain', urlparse(url).netloc),
                political_bias=source_info['bias'],
                publication_date=pub_date,
                authors=authors
            )
            
            logger.info(f"Successfully extracted article: {title[:50]}...")
            return article
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {e}")
            return None
    
    async def parse_rss_feed(self, feed_url: str, source_info: Dict) -> List[RSSFeedItem]:
        """Parse RSS feed and return feed items."""
        try:
            response = self.session.get(feed_url, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            items = []
            for entry in feed.entries:
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    # Create RSSFeedItem
                    item = RSSFeedItem(
                        title=entry.title,
                        link=entry.link,
                        description=getattr(entry, 'description', ''),
                        published=pub_date,
                        source=source_info['name'],
                        domain=source_info.get('search_domain', urlparse(entry.link).netloc),
                        political_bias=source_info['bias']
                    )
                    items.append(item)
                    
                except Exception as e:
                    logger.error(f"Error parsing RSS item: {e}")
                    continue
            
            logger.info(f"Parsed {len(items)} items from RSS feed: {source_info['name']}")
            return items
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            return []
    
    async def get_recent_rss_articles(self, hours: int = 24) -> List[RSSFeedItem]:
        """Get recent articles from all RSS feeds."""
        all_feeds = get_all_rss_feeds()
        recent_items = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for feed_info in all_feeds:
            try:
                source_info = {
                    'name': feed_info['source'],
                    'bias': feed_info['bias'],
                    'search_domain': feed_info['domain']
                }
                
                items = await self.parse_rss_feed(feed_info['url'], source_info)
                
                # Filter for recent items
                for item in items:
                    if item.published and item.published > cutoff_time:
                        recent_items.append(item)
                    elif not item.published:  # Include items without date
                        recent_items.append(item)
                        
            except Exception as e:
                logger.error(f"Error processing RSS feed {feed_info['url']}: {e}")
                continue
        
        logger.info(f"Found {len(recent_items)} recent RSS items")
        return recent_items
    
    async def search_web_for_topic(self, query: str, max_results: int = 20) -> List[SearchResult]:
        """Search the web for articles related to a topic using Serper API."""
        try:
            url = "https://google.serper.dev/search"
            
            # Create search query with Swedish news sites
            swedish_domains = " OR ".join([f"site:{domain}" for domain in settings.SWEDISH_NEWS_SOURCES.keys()])
            search_query = f"{query} ({swedish_domains})"
            
            payload = {
                "q": search_query,
                "gl": "se",  # Sweden
                "hl": "sv",  # Swedish
                "num": max_results,
                "tbm": "nws"  # News search
            }
            
            headers = {
                "X-API-KEY": settings.SERPER_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            search_results = []
            for item in data.get('news', []):
                try:
                    # Parse date if available
                    pub_date = None
                    if 'date' in item:
                        try:
                            pub_date = datetime.fromisoformat(item['date'])
                        except:
                            pass
                    
                    result = SearchResult(
                        title=item['title'],
                        url=item['link'],
                        snippet=item.get('snippet', ''),
                        date=pub_date
                    )
                    search_results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error parsing search result: {e}")
                    continue
            
            logger.info(f"Found {len(search_results)} search results for query: {query}")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching web for topic '{query}': {e}")
            return []
    
    async def extract_articles_from_search_results(
        self, 
        search_results: List[SearchResult]
    ) -> List[NewsArticle]:
        """Extract full articles from search results."""
        articles = []
        
        for result in search_results:
            try:
                # Determine source info from URL
                domain = urlparse(result.url).netloc.lower()
                
                # Find matching source info
                source_info = None
                for source_domain, info in settings.SWEDISH_NEWS_SOURCES.items():
                    if source_domain in domain or domain in source_domain:
                        source_info = info
                        break
                
                if not source_info:
                    logger.warning(f"Unknown source domain: {domain}")
                    continue
                
                # Extract article content
                article = await self.extract_article_content(result.url, source_info)
                if article:
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Error extracting article from search result {result.url}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(articles)} articles from search results")
        return articles
    
    async def find_articles_for_topic(self, topic: str) -> List[NewsArticle]:
        """Find articles for a given topic using both search and RSS."""
        all_articles = []
        
        # Search the web
        search_results = await self.search_web_for_topic(topic)
        search_articles = await self.extract_articles_from_search_results(search_results)
        all_articles.extend(search_articles)
        
        # Check recent RSS items (last 24 hours)
        rss_items = await self.get_recent_rss_articles(hours=24)
        
        # Filter RSS items that match the topic
        relevant_rss_items = []
        for item in rss_items:
            if (topic.lower() in item.title.lower() or 
                topic.lower() in item.description.lower()):
                relevant_rss_items.append(item)
        
        # Extract articles from relevant RSS items
        for item in relevant_rss_items:
            source_info = None
            for domain, info in settings.SWEDISH_NEWS_SOURCES.items():
                if info['name'] == item.source:
                    source_info = info
                    break
            
            if source_info:
                article = await self.extract_article_content(item.link, source_info)
                if article:
                    all_articles.append(article)
        
        # Remove duplicates based on URL
        unique_articles = []
        seen_urls = set()
        for article in all_articles:
            if str(article.url) not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(str(article.url))
        
        logger.info(f"Found {len(unique_articles)} unique articles for topic: {topic}")
        return unique_articles


# Global instance
web_scraper = WebScraper() 