"""
LLM Manager for Google Gemini integration using LangChain.
Handles all AI processing tasks including bias analysis and summarization.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
from google.generativeai.types import ThinkingConfig, GenerationConfig

from ..config.settings import settings
from ..models.news_models import (
    NewsArticle, BiasSpecificSummary, NeutralSummary, 
    VectorStoreEntry, BiasVisualizationData
)
from ..prompts.bias_analysis_prompts import (
    get_bias_analysis_prompt, get_neutral_summary_prompt,
    get_key_facts_prompt, get_internal_linking_prompt,
    BIAS_ANALYSIS_CHAT_PROMPT
)

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages all LLM interactions using Google Gemini via LangChain."""
    
    def __init__(self):
        """Initialize the LLM manager with Google Gemini 2.5 Flash configuration."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.0,  # Low creativity for factual reporting
            max_tokens=settings.MAX_TOKENS,
            convert_system_message_to_human=True,
            generation_config=GenerationConfig(
                thinking_config=ThinkingConfig(thinking_budget=0)  # Disable reasoning tokens
            )
        )
        
        # Create chains for different tasks
        self._initialize_chains()
    
    def _initialize_chains(self) -> None:
        """Initialize LangChain chains for different processing tasks."""
        # Bias analysis chains for each political leaning
        self.bias_analysis_chains = {}
        for bias in ["Left", "Center", "Right"]:
            prompt = get_bias_analysis_prompt(bias)
            self.bias_analysis_chains[bias] = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=settings.DEBUG
            )
        
        # Neutral summary chain
        self.neutral_summary_chain = LLMChain(
            llm=self.llm,
            prompt=get_neutral_summary_prompt(),
            verbose=settings.DEBUG
        )
        
        # Key facts extraction chain
        self.key_facts_chain = LLMChain(
            llm=self.llm,
            prompt=get_key_facts_prompt(),
            verbose=settings.DEBUG
        )
        
        # Internal linking chain
        self.internal_linking_chain = LLMChain(
            llm=self.llm,
            prompt=get_internal_linking_prompt(),
            verbose=settings.DEBUG
        )
    
    async def process_all_bias_summaries(self, articles: List[NewsArticle]) -> List[BiasSpecificSummary]:
        """
        Generate bias-specific summaries for all political leanings present in the articles.
        
        Args:
            articles: List of news articles with political bias labels
            
        Returns:
            List of bias-specific summaries for each political leaning
        """
        try:
            # Group articles by political bias
            articles_by_bias = self._group_articles_by_bias(articles)
            
            bias_summaries = []
            
            # Generate summary for each bias type
            for bias in ["Left", "Center", "Right"]:
                bias_articles = articles_by_bias.get(bias, [])
                
                if bias_articles:
                    # Generate summary for this bias
                    summary_text = await self._generate_bias_summary(bias, bias_articles)
                    
                    bias_summary = BiasSpecificSummary(
                        political_bias=bias,
                        summary=summary_text,
                        article_count=len(bias_articles),
                        sources=[article.source_name for article in bias_articles]
                    )
                else:
                    # Create empty summary for bias not present
                    bias_summary = BiasSpecificSummary(
                        political_bias=bias,
                        summary=f"Inga {bias.lower()}-orienterade källor rapporterade om detta ämne.",
                        article_count=0,
                        sources=[]
                    )
                
                bias_summaries.append(bias_summary)
            
            logger.info(f"Generated {len(bias_summaries)} bias summaries")
            return bias_summaries
            
        except Exception as e:
            logger.error(f"Error processing bias summaries: {e}")
            return []
    
    async def generate_neutral_summary(
        self, 
        articles: List[NewsArticle], 
        related_context: List[VectorStoreEntry], 
        topic: str
    ) -> NeutralSummary:
        """
        Generate a neutral summary enhanced by RAG context.
        
        Args:
            articles: Current articles about the topic
            related_context: Related articles from vector database
            topic: The news topic being analyzed
            
        Returns:
            Neutral summary with key facts and internal links
        """
        try:
            # Prepare articles text
            articles_text = self._format_articles_for_prompt(articles)
            
            # Prepare related context text
            context_text = self._format_context_for_prompt(related_context)
            
            # Generate neutral summary
            summary_result = await self.neutral_summary_chain.arun(
                articles=articles_text,
                related_context=context_text,
                topic=topic
            )
            
            # Extract key facts
            key_facts = await self._extract_key_facts(articles_text, summary_result)
            
            # Generate internal links
            internal_links = await self._generate_internal_links(topic, related_context)
            
            neutral_summary = NeutralSummary(
                summary=summary_result.strip(),
                key_facts=key_facts,
                related_context=[entry.content[:200] + "..." for entry in related_context[:3]],
                internal_links=internal_links
            )
            
            logger.info("Generated neutral summary with RAG enhancement")
            return neutral_summary
            
        except Exception as e:
            logger.error(f"Error generating neutral summary: {e}")
            return NeutralSummary(
                summary=f"Kunde inte generera neutral sammanfattning: {str(e)}",
                key_facts=[],
                related_context=[],
                internal_links=[]
            )
    
    async def generate_bias_visualization_data(self, articles: List[NewsArticle]) -> List[BiasVisualizationData]:
        """
        Generate data for bias visualization component.
        
        Args:
            articles: List of news articles
            
        Returns:
            List of visualization data for each article
        """
        try:
            visualization_data = []
            
            for article in articles:
                viz_data = BiasVisualizationData(
                    source_name=article.source_name,
                    bias=article.political_bias,
                    url=article.url
                )
                visualization_data.append(viz_data)
            
            logger.info(f"Generated bias visualization data for {len(articles)} articles")
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error generating bias visualization data: {e}")
            return []
    
    def _group_articles_by_bias(self, articles: List[NewsArticle]) -> Dict[str, List[NewsArticle]]:
        """Group articles by their political bias."""
        grouped = {"Left": [], "Center": [], "Right": []}
        
        for article in articles:
            if article.political_bias in grouped:
                grouped[article.political_bias].append(article)
        
        return grouped
    
    async def _generate_bias_summary(self, bias: str, articles: List[NewsArticle]) -> str:
        """Generate summary for a specific political bias."""
        try:
            # Format articles for prompt
            articles_text = self._format_articles_for_prompt(articles)
            
            # Use the appropriate bias analysis chain
            chain = self.bias_analysis_chains[bias]
            summary = await chain.arun(
                articles=articles_text,
                bias_type=bias
            )
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating {bias} bias summary: {e}")
            return f"Kunde inte generera sammanfattning för {bias}-orienterade källor."
    
    def _format_articles_for_prompt(self, articles: List[NewsArticle]) -> str:
        """Format articles for use in prompts."""
        formatted_articles = []
        
        for i, article in enumerate(articles[:10], 1):  # Limit to 10 articles to avoid token limits
            formatted_article = f"""
Artikel {i}:
Källa: {article.source_name} ({article.political_bias})
Titel: {article.title}
Innehåll: {article.content[:1000]}...
URL: {article.url}
---
"""
            formatted_articles.append(formatted_article)
        
        return "\n".join(formatted_articles)
    
    def _format_context_for_prompt(self, context_entries: List[VectorStoreEntry]) -> str:
        """Format context entries for use in prompts."""
        if not context_entries:
            return "Ingen relevant historisk kontext hittades."
        
        formatted_context = []
        
        for i, entry in enumerate(context_entries[:5], 1):  # Limit to 5 context entries
            formatted_entry = f"""
Kontext {i}:
{entry.content[:500]}...
---
"""
            formatted_context.append(formatted_entry)
        
        return "\n".join(formatted_context)
    
    async def _extract_key_facts(self, articles_text: str, summary: str) -> List[str]:
        """Extract key facts from articles and summary."""
        try:
            facts_result = await self.key_facts_chain.arun(
                articles=articles_text,
                summary=summary
            )
            
            # Parse the facts (assuming they're returned as a bullet-point list)
            facts = [
                fact.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                for fact in facts_result.split('\n')
                if fact.strip() and not fact.strip().startswith('Viktiga fakta')
            ]
            
            return facts[:5]  # Limit to 5 key facts
            
        except Exception as e:
            logger.error(f"Error extracting key facts: {e}")
            return []
    
    async def _generate_internal_links(self, topic: str, related_context: List[VectorStoreEntry]) -> List[Dict[str, str]]:
        """Generate internal links from related context."""
        try:
            if not related_context:
                return []
            
            # Create internal links from related context
            internal_links = []
            
            for entry in related_context[:3]:  # Limit to 3 internal links
                # Extract title and URL from metadata
                metadata = entry.metadata
                if 'title' in metadata and 'url' in metadata:
                    internal_links.append({
                        'title': metadata['title'],
                        'url': metadata['url']
                    })
            
            return internal_links
            
        except Exception as e:
            logger.error(f"Error generating internal links: {e}")
            return []


# Global instance
llm_manager = LLMManager() 