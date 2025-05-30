"""
Prompt templates for political bias analysis and news summarization.
Uses LangChain's PromptTemplate system for consistent prompt management.
"""

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate


# Template for analyzing political bias in news reporting
BIAS_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["articles", "bias_type"],
    template="""
You are an expert political analyst specializing in Swedish media and political perspectives. 
Your task is to analyze how {bias_type}-leaning Swedish news sources are reporting on a specific topic.

IMPORTANT GUIDELINES:
1. Focus on HOW the {bias_type} sources are framing and reporting the story
2. Capture the perspective, tone, and emphasis unique to {bias_type} reporting
3. Do NOT compare to other political biases in this summary
4. Reflect the actual reporting style and viewpoint of {bias_type} sources
5. Be factual but capture the specific angle and emphasis

Articles from {bias_type} sources:
{articles}

Based on these articles, write a concise summary (150-200 words) that captures:
- The key points being emphasized by {bias_type} sources
- The tone and framing used in their reporting
- Specific angles or perspectives highlighted
- Any particular concerns or priorities reflected in the coverage

Summary of what {bias_type} sources are saying:
"""
)

# Template for generating neutral summaries with RAG context
NEUTRAL_SUMMARY_PROMPT = PromptTemplate(
    input_variables=["articles", "related_context", "topic"],
    template="""
You are a professional journalist tasked with creating a completely neutral, factual summary of a news topic.

TOPIC: {topic}

CURRENT ARTICLES (from all political perspectives):
{articles}

RELEVANT HISTORICAL CONTEXT (from knowledge base):
{related_context}

INSTRUCTIONS:
1. Create a comprehensive, strictly neutral summary that presents only verifiable facts
2. Use the historical context to provide background and depth
3. Avoid any political bias, speculation, or subjective language
4. Focus on core facts, key developments, and verified information
5. Include relevant background from historical context when it adds factual depth
6. Structure the summary logically with clear, factual statements
7. Length: 300-400 words

Key elements to include:
- What happened (core facts)
- When and where it occurred
- Who is involved (key parties, officials, organizations)
- Why it matters (impact, significance)
- Relevant background context from historical sources
- Current status or developments

Write a neutral, fact-based news summary:
"""
)

# Template for extracting key facts from articles
KEY_FACTS_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["article_content"],
    template="""
Extract the key factual points from this news article. Focus on verifiable facts only.

Article Content:
{article_content}

Extract 3-5 key facts in bullet point format:
- [Fact 1: What happened]
- [Fact 2: When/Where]
- [Fact 3: Who is involved]
- [Fact 4: Current status]
- [Fact 5: Impact/Significance]

Key Facts:
"""
)

# Template for identifying internal linking opportunities
INTERNAL_LINKING_PROMPT = PromptTemplate(
    input_variables=["current_topic", "related_articles"],
    template="""
You are analyzing related articles to identify valuable internal linking opportunities for SEO and reader engagement.

CURRENT TOPIC: {current_topic}

RELATED ARTICLES FROM KNOWLEDGE BASE:
{related_articles}

Identify the 3-5 most relevant articles that would provide valuable context or background for readers interested in the current topic.

For each recommended article, provide:
1. Title of the related article
2. Brief explanation of how it relates to the current topic
3. URL if available

Format as a JSON list:
[
  {{
    "title": "Article title",
    "relevance": "Brief explanation of relevance",
    "url": "URL if available"
  }}
]

Internal linking recommendations:
"""
)

# Template for WordPress post formatting
WORDPRESS_POST_PROMPT = PromptTemplate(
    input_variables=["neutral_summary", "bias_summaries", "topic", "internal_links"],
    template="""
Format this news analysis for WordPress publication.

TOPIC: {topic}
NEUTRAL SUMMARY: {neutral_summary}
BIAS SUMMARIES: {bias_summaries}
INTERNAL LINKS: {internal_links}

Create a well-formatted WordPress post with:
1. Compelling headline
2. Meta description (150 chars)
3. Main content with proper HTML formatting
4. Suggested tags
5. Internal links integrated naturally

WordPress Post Content:
"""
)

# Few-shot example for bias analysis
BIAS_ANALYSIS_EXAMPLES = [
    {
        "input": "Left sources reporting on tax policy",
        "output": "Left-leaning sources are emphasizing the social justice aspects of the proposed tax reforms, highlighting how the changes will reduce inequality and fund essential public services. Their coverage focuses on the benefits for working families and the need for wealthy individuals and corporations to pay their fair share. The reporting frames the policy as a necessary step toward economic fairness, with extensive coverage of how the reforms will strengthen healthcare and education funding."
    },
    {
        "input": "Right sources reporting on tax policy", 
        "output": "Right-leaning sources are focusing on the economic implications of the tax reforms, particularly concerns about competitiveness and business investment. Their coverage emphasizes potential negative impacts on entrepreneurship, job creation, and economic growth. The reporting highlights warnings from business leaders about companies potentially relocating, and frames the debate around maintaining Sweden's economic competitiveness in the global market."
    }
]

BIAS_ANALYSIS_FEW_SHOT = FewShotPromptTemplate(
    examples=BIAS_ANALYSIS_EXAMPLES,
    example_prompt=PromptTemplate(
        input_variables=["input", "output"],
        template="Input: {input}\nOutput: {output}"
    ),
    prefix="Here are examples of how to analyze political bias in news reporting:",
    suffix="Input: {bias_type} sources reporting on {topic}\nOutput:",
    input_variables=["bias_type", "topic"]
)

# Chat template for interactive bias analysis
BIAS_ANALYSIS_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert analyst of Swedish political media. Your task is to analyze how different political perspectives report on news topics. Focus on the framing, emphasis, and perspective rather than comparing biases."""),
    ("human", """Analyze how {bias_type} sources are reporting on this topic:

Articles: {articles}

Provide a summary that captures the {bias_type} perspective and framing.""")
])

def get_bias_analysis_prompt(bias_type: str) -> PromptTemplate:
    """Get the appropriate bias analysis prompt for a given bias type."""
    return BIAS_ANALYSIS_PROMPT.partial(bias_type=bias_type)

def get_neutral_summary_prompt() -> PromptTemplate:
    """Get the neutral summary prompt template."""
    return NEUTRAL_SUMMARY_PROMPT

def get_key_facts_prompt() -> PromptTemplate:
    """Get the key facts extraction prompt template."""
    return KEY_FACTS_EXTRACTION_PROMPT

def get_internal_linking_prompt() -> PromptTemplate:
    """Get the internal linking prompt template."""
    return INTERNAL_LINKING_PROMPT

def get_wordpress_post_prompt() -> PromptTemplate:
    """Get the WordPress post formatting prompt template."""
    return WORDPRESS_POST_PROMPT 