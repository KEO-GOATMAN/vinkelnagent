"""
Configuration settings for the News Agent application.
Manages environment variables and application constants.
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    
    # WordPress Configuration
    WORDPRESS_URL: str = os.getenv("WORDPRESS_URL", "")
    WORDPRESS_USERNAME: str = os.getenv("WORDPRESS_USERNAME", "")
    WORDPRESS_PASSWORD: str = os.getenv("WORDPRESS_PASSWORD", "")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Vector Database Settings
    VECTOR_TABLE_NAME: str = "news_articles"
    VECTOR_DIMENSION: int = 384  # sentence-transformers/all-MiniLM-L6-v2
    
    # LLM Settings
    GEMINI_MODEL: str = "gemini-2.5-flash-preview-05-20"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.0
    
    @classmethod
    def validate_required_settings(cls) -> None:
        """Validate that all required environment variables are set."""
        required_vars = [
            "GEMINI_API_KEY",
            "SUPABASE_URL", 
            "SUPABASE_ANON_KEY",
            "SERPER_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Swedish News Sources with Political Bias Mapping
SWEDISH_NEWS_SOURCES: Dict[str, Dict] = {
    # Left-leaning sources
    "aftonbladet.se": {
        "name": "Aftonbladet",
        "bias": "Left",
        "rss_feed": "https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/",
        "search_domain": "aftonbladet.se"
    },
    "expressen.se": {
        "name": "Expressen", 
        "bias": "Left",
        "rss_feed": "https://feeds.expressen.se/nyheter/",
        "search_domain": "expressen.se"
    },
    
    # Center sources
    "dn.se": {
        "name": "Dagens Nyheter",
        "bias": "Center",
        "rss_feed": "https://www.dn.se/rss/",
        "search_domain": "dn.se"
    },
    "svt.se": {
        "name": "SVT Nyheter",
        "bias": "Center", 
        "rss_feed": "https://www.svt.se/nyheter/rss.xml",
        "search_domain": "svt.se"
    },
    "sr.se": {
        "name": "Sveriges Radio",
        "bias": "Center",
        "rss_feed": "https://api.sr.se/api/rss/news",
        "search_domain": "sr.se"
    },
    
    # Right-leaning sources
    "svenskadagbladet.se": {
        "name": "Svenska Dagbladet",
        "bias": "Right",
        "rss_feed": "https://www.svd.se/feed/articles.rss",
        "search_domain": "svenskadagbladet.se"
    },
    "gp.se": {
        "name": "Göteborgs-Posten",
        "bias": "Right", 
        "rss_feed": "https://www.gp.se/nyheter/rss",
        "search_domain": "gp.se"
    }
}

# Initialize settings instance
settings = Settings()

def get_sources_by_bias(bias: str) -> List[Dict]:
    """Get news sources filtered by political bias."""
    return [
        {"domain": domain, **source_info} 
        for domain, source_info in SWEDISH_NEWS_SOURCES.items() 
        if source_info["bias"] == bias
    ]

def get_all_rss_feeds() -> List[Dict]:
    """Get all RSS feed URLs with source information."""
    return [
        {
            "url": source_info["rss_feed"],
            "source": source_info["name"],
            "bias": source_info["bias"],
            "domain": domain
        }
        for domain, source_info in SWEDISH_NEWS_SOURCES.items()
    ] 