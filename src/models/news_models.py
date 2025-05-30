"""
Data models for the News Agent application.
Uses Pydantic for data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class NewsArticle(BaseModel):
    """Represents a single news article."""
    
    title: str
    content: str
    url: HttpUrl
    source: str
    source_name: Optional[str] = None  # Alias for source for compatibility
    domain: str
    political_bias: str = Field(..., pattern="^(Left|Center|Right)$")
    publication_date: Optional[datetime] = None
    authors: List[str] = []
    summary: Optional[str] = None
    keywords: List[str] = []
    
    def __init__(self, **data):
        # If source_name is not provided, use source
        if 'source_name' not in data and 'source' in data:
            data['source_name'] = data['source']
        # If source is not provided, use source_name
        elif 'source' not in data and 'source_name' in data:
            data['source'] = data['source_name']
        super().__init__(**data)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: str
        }


class ProcessingInput(BaseModel):
    """Input for news topic processing."""
    
    topic_title: Optional[str] = None
    topic_url: Optional[HttpUrl] = None
    topic_description: Optional[str] = None
    
    def get_search_query(self) -> str:
        """Generate a search query from the input."""
        if self.topic_title:
            return self.topic_title
        elif self.topic_description:
            return self.topic_description
        elif self.topic_url:
            return str(self.topic_url)
        else:
            raise ValueError("At least one input field must be provided")


class BiasSpecificSummary(BaseModel):
    """Summary from a specific political perspective."""
    
    political_bias: str = Field(..., pattern="^(Left|Center|Right)$")
    summary: str
    article_count: int
    sources: List[str]
    
    
class BiasVisualizationData(BaseModel):
    """Data for political bias visualization."""
    
    source_name: str
    bias: str = Field(..., pattern="^(Left|Center|Right)$")
    url: HttpUrl


class NeutralSummary(BaseModel):
    """Neutral summary enhanced by RAG."""
    
    summary: str
    key_facts: List[str]
    related_context: List[str] = []  # From RAG retrieval
    internal_links: List[HttpUrl] = []
    

class ProcessingResult(BaseModel):
    """Complete result of news processing."""
    
    topic: str
    neutral_summary: NeutralSummary
    bias_summaries: List[BiasSpecificSummary]
    bias_visualization_data: List[BiasVisualizationData]
    articles_processed: List[NewsArticle]
    processing_timestamp: datetime
    wordpress_post_id: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: str
        }


class VectorStoreEntry(BaseModel):
    """Entry for vector database storage."""
    
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RSSFeedItem(BaseModel):
    """Represents an item from an RSS feed."""
    
    title: str
    link: HttpUrl
    description: str
    published: Optional[datetime] = None
    source: str
    domain: str
    political_bias: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: str
        }


class SearchResult(BaseModel):
    """Represents a web search result."""
    
    title: str
    url: HttpUrl
    snippet: str
    date: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: str
        } 