"""
Supabase vector store integration for news articles.
Handles embedding storage, retrieval, and similarity search.
"""

import asyncio
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import logging

from ..config.settings import settings
from ..models.news_models import NewsArticle, VectorStoreEntry

logger = logging.getLogger(__name__)


class SupabaseVectorStore:
    """Vector store implementation using Supabase with pg_vector."""
    
    def __init__(self):
        """Initialize the Supabase vector store."""
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384
        
        # Table existence will be ensured when first used
        self._table_checked = False
    
    async def _ensure_table_exists(self) -> None:
        """Ensure the vector table exists with proper schema."""
        if self._table_checked:
            return
            
        try:
            # Check if table exists and create if needed
            result = self.client.table(settings.VECTOR_TABLE_NAME).select("id").limit(1).execute()
            logger.info(f"Vector table '{settings.VECTOR_TABLE_NAME}' exists and is accessible")
            self._table_checked = True
        except Exception as e:
            logger.warning(f"Vector table may not exist or is not accessible: {e}")
            # Note: Table creation should be handled by database setup script
            self._table_checked = True
    
    def _generate_content_id(self, content: str, url: str) -> str:
        """Generate a unique ID for content based on URL and content hash."""
        content_hash = hashlib.sha256(f"{url}{content}".encode()).hexdigest()[:16]
        return f"article_{content_hash}"
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using sentence transformer."""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    async def add_article(self, article: NewsArticle) -> str:
        """Add a news article to the vector store."""
        try:
            # Ensure table exists
            await self._ensure_table_exists()
            
            # Create content for embedding (title + summary of content)
            content_for_embedding = f"{article.title}\n\n{article.content[:1000]}"
            
            # Generate embedding
            embedding = self._create_embedding(content_for_embedding)
            
            # Create unique ID
            article_id = self._generate_content_id(article.content, str(article.url))
            
            # Prepare metadata
            metadata = {
                "title": article.title,
                "url": str(article.url),
                "source": article.source,
                "domain": article.domain,
                "political_bias": article.political_bias,
                "publication_date": article.publication_date.isoformat() if article.publication_date else None,
                "authors": article.authors,
                "keywords": article.keywords
            }
            
            # Insert into Supabase
            data = {
                "id": article_id,
                "content": content_for_embedding,
                "metadata": metadata,
                "embedding": embedding,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table(settings.VECTOR_TABLE_NAME).upsert(data).execute()
            
            logger.info(f"Added article to vector store: {article.title[:50]}...")
            return article_id
            
        except Exception as e:
            logger.error(f"Error adding article to vector store: {e}")
            raise
    
    async def add_articles_batch(self, articles: List[NewsArticle]) -> List[str]:
        """Add multiple articles to the vector store in batch."""
        article_ids = []
        
        for article in articles:
            try:
                article_id = await self.add_article(article)
                article_ids.append(article_id)
            except Exception as e:
                logger.error(f"Error adding article {article.title}: {e}")
                continue
        
        logger.info(f"Added {len(article_ids)} articles to vector store")
        return article_ids
    
    async def similarity_search(
        self, 
        query: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[VectorStoreEntry, float]]:
        """Perform similarity search to find related articles."""
        try:
            # Ensure table exists
            await self._ensure_table_exists()
            
            # Create embedding for query
            query_embedding = self._create_embedding(query)
            
            # Perform similarity search using Supabase RPC function
            # Note: This requires a custom function in Supabase
            result = self.client.rpc(
                'match_news_articles',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': similarity_threshold,
                    'match_count': limit
                }
            ).execute()
            
            # Parse results
            matches = []
            for row in result.data:
                entry = VectorStoreEntry(
                    id=row['id'],
                    content=row['content'],
                    metadata=row['metadata'],
                    embedding=row['embedding'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                similarity_score = row.get('similarity', 0.0)
                matches.append((entry, similarity_score))
            
            logger.info(f"Found {len(matches)} similar articles for query: {query[:50]}...")
            return matches
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            return []
    
    async def get_recent_articles(
        self, 
        days: int = 30, 
        limit: int = 100
    ) -> List[VectorStoreEntry]:
        """Get recently added articles from the vector store."""
        try:
            cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - days)
            
            result = self.client.table(settings.VECTOR_TABLE_NAME)\
                .select("*")\
                .gte("created_at", cutoff_date.isoformat())\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            articles = []
            for row in result.data:
                entry = VectorStoreEntry(
                    id=row['id'],
                    content=row['content'],
                    metadata=row['metadata'],
                    embedding=row['embedding'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                articles.append(entry)
            
            logger.info(f"Retrieved {len(articles)} recent articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error retrieving recent articles: {e}")
            return []
    
    async def get_articles_by_bias(self, bias: str) -> List[VectorStoreEntry]:
        """Get articles filtered by political bias."""
        try:
            result = self.client.table(settings.VECTOR_TABLE_NAME)\
                .select("*")\
                .eq("metadata->>political_bias", bias)\
                .order("created_at", desc=True)\
                .execute()
            
            articles = []
            for row in result.data:
                entry = VectorStoreEntry(
                    id=row['id'],
                    content=row['content'],
                    metadata=row['metadata'],
                    embedding=row['embedding'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                articles.append(entry)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error retrieving articles by bias {bias}: {e}")
            return []
    
    async def delete_article(self, article_id: str) -> bool:
        """Delete an article from the vector store."""
        try:
            result = self.client.table(settings.VECTOR_TABLE_NAME)\
                .delete()\
                .eq("id", article_id)\
                .execute()
            
            logger.info(f"Deleted article {article_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting article {article_id}: {e}")
            return False


# Global instance
vector_store = SupabaseVectorStore() 