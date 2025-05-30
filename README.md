# Automated Politically-Aware News Summarization & Publishing Agent

An intelligent news agent that leverages Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to monitor Swedish news topics, analyze reporting across political biases, generate neutral summaries, and publish to WordPress - all while maintaining an internal knowledge base for contextual enhancement.

## 🎯 Features

### Core Functionality
- **Multi-Source News Monitoring**: Tracks Swedish news outlets across the political spectrum
- **Political Bias Analysis**: Generates perspective-specific summaries from Left, Center, and Right sources
- **RAG-Enhanced Neutral Summaries**: Creates factual, comprehensive summaries using historical context
- **Automated WordPress Publishing**: Posts complete analysis with bias visualization
- **RSS Feed Processing**: Continuous monitoring via Vercel cron jobs
- **Vector Knowledge Base**: Stores articles for contextual enhancement and internal linking

### Technical Features
- **Serverless Architecture**: Built for Vercel deployment with optimal cold-start performance
- **Supabase Vector Database**: Uses pg_vector for similarity search and retrieval
- **Google Gemini Integration**: Powered by advanced LLM capabilities via LangChain
- **Swedish News Source Mapping**: Pre-configured bias classifications for major outlets

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vercel API    │    │   News Sources   │    │   Supabase      │
│   Functions     │◄──►│   (RSS/Web)      │    │   Vector DB     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Google        │    │   Content        │    │   WordPress     │
│   Gemini LLM    │    │   Processing     │    │   Publishing    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** (for Vercel CLI)
- **Python 3.9+** (runtime compatibility)
- **Supabase Account** (for vector database)
- **Google AI Studio** (for Gemini API key)
- **Serper.dev Account** (for web search)
- **WordPress Site** (with REST API enabled)

### 1. Local Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd news-agent

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys (see Configuration section)
```

### 2. Supabase Database Setup

1. **Create a Supabase project** at [supabase.com](https://supabase.com)

2. **Enable pg_vector extension**:
   - Go to Database → Extensions in Supabase dashboard
   - Search for "vector" and enable the extension

3. **Run the setup script**:
   - Go to SQL Editor in Supabase dashboard
   - Copy and paste the contents of `setup/supabase_setup.sql`
   - Execute the script

4. **Get your credentials**:
   - Project URL: Found in Settings → API
   - Anon Key: Found in Settings → API

### 3. API Keys Configuration

Create a `.env` file with the following variables:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Web Search API (Serper.dev)
SERPER_API_KEY=your_serper_api_key

# WordPress Configuration
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your_wp_username
WORDPRESS_PASSWORD=your_wp_app_password

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

### 4. Local Testing

```bash
# Test the main processing function
python api/process_news_topic.py

# Test RSS processing
python api/check_rss_feeds.py
```

### 5. Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Set environment variables
vercel env add GEMINI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add SERPER_API_KEY
vercel env add WORDPRESS_URL
vercel env add WORDPRESS_USERNAME
vercel env add WORDPRESS_PASSWORD

# Deploy
vercel --prod
```

## 📖 Usage

### Processing a News Topic

Send a POST request to `/api/process_news_topic`:

```bash
curl -X POST https://your-vercel-app.vercel.app/api/process_news_topic \
  -H "Content-Type: application/json" \
  -d '{
    "topic_title": "Swedish Election Results",
    "topic_description": "Analysis of the latest Swedish parliamentary election"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "data": {
    "topic": "Swedish Election Results",
    "neutral_summary": {
      "summary": "Comprehensive neutral analysis...",
      "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
      "internal_links": [{"title": "Related Article", "url": "..."}]
    },
    "bias_summaries": [
      {
        "political_bias": "Left",
        "summary": "Left-leaning perspective...",
        "article_count": 3,
        "sources": ["Aftonbladet", "Expressen"]
      }
    ],
    "bias_visualization_data": [...],
    "wordpress_post_id": 123
  }
}
```

### RSS Feed Monitoring

The system automatically processes RSS feeds every 6 hours via Vercel cron jobs. Manual trigger:

```bash
curl https://your-vercel-app.vercel.app/api/check_rss_feeds
```

### Health Check

```bash
curl https://your-vercel-app.vercel.app/api/check_rss_feeds/health
```

## 🔧 Configuration

### Swedish News Sources

The system is pre-configured with major Swedish news outlets:

**Left-leaning sources:**
- Aftonbladet
- Expressen

**Center sources:**
- Dagens Nyheter
- SVT Nyheter
- Sveriges Radio

**Right-leaning sources:**
- Svenska Dagbladet
- Göteborgs-Posten

### Customization

To add new sources, edit `src/config/settings.py`:

```python
SWEDISH_NEWS_SOURCES = {
    "new-source.se": {
        "name": "New Source",
        "bias": "Center",
        "rss_feed": "https://new-source.se/rss",
        "search_domain": "new-source.se"
    }
}
```

## 🏢 Project Structure

```
news-agent/
├── api/                          # Vercel serverless functions
│   ├── process_news_topic.py     # Main processing endpoint
│   └── check_rss_feeds.py        # RSS monitoring cron job
├── src/                          # Source code
│   ├── agents/                   # Main orchestration
│   │   └── news_agent.py         # NewsAgent class
│   ├── components/               # Core components
│   │   └── llm_manager.py        # Gemini LLM integration
│   ├── config/                   # Configuration
│   │   └── settings.py           # Settings and constants
│   ├── models/                   # Data models
│   │   └── news_models.py        # Pydantic models
│   ├── prompts/                  # LLM prompts
│   │   └── bias_analysis_prompts.py
│   ├── utils/                    # Utilities
│   │   ├── web_scraper.py        # Web scraping
│   │   └── wordpress_publisher.py # WordPress integration
│   └── vectorstores/             # Vector database
│       └── supabase_store.py     # Supabase integration
├── setup/                        # Setup scripts
│   └── supabase_setup.sql        # Database schema
├── .env.example                  # Environment template
├── vercel.json                   # Vercel configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🛠️ Development

### Adding New Features

1. **New Analysis Types**: Extend `LLMManager` with new prompt templates
2. **Additional Sources**: Update `SWEDISH_NEWS_SOURCES` in settings
3. **Custom Outputs**: Modify `ProcessingResult` model and WordPress publisher

### Testing

```bash
# Unit tests (implement as needed)
python -m pytest tests/

# Integration tests
python tests/test_integration.py

# Load testing
python tests/test_performance.py
```

### Monitoring

- **Vercel Logs**: Monitor function execution and errors
- **Supabase Logs**: Track database performance
- **WordPress**: Monitor successful publications

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Ensure PYTHONPATH includes src directory
export PYTHONPATH="${PYTHONPATH}:src"
```

**2. Supabase Connection Issues**
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Check if pg_vector extension is enabled
- Ensure network connectivity

**3. LLM Rate Limits**
- Monitor Gemini API usage
- Implement exponential backoff for retries
- Consider request batching

**4. RSS Feed Parsing**
- Some feeds may require custom parsing
- Check feed validity with online validators
- Verify SSL certificates for HTTPS feeds

## 📊 Performance Optimization

### Vercel Function Optimization
- **Cold Start**: Minimize imports and initialization
- **Memory Usage**: Monitor and adjust function memory allocation
- **Timeout**: Adjust based on processing complexity

### Database Optimization
- **Vector Search**: Tune `lists` parameter for IVFFlat index
- **Batch Operations**: Use batch inserts for multiple articles
- **Connection Pooling**: Implement for high-volume usage

### LLM Optimization
- **Context Management**: Limit article content length for prompts
- **Parallel Processing**: Process bias summaries concurrently
- **Caching**: Cache embeddings and frequent results

## 🔐 Security Considerations

### Environment Variables
- Use Vercel's encrypted environment variables
- Rotate API keys regularly
- Implement least-privilege access

### Database Security
- Use Row Level Security (RLS) in Supabase
- Implement proper authentication for sensitive operations
- Regular security audits

### WordPress Security
- Use Application Passwords instead of regular passwords
- Implement HTTPS for all communications
- Monitor for unauthorized posts

## 📈 Scaling

### High Volume Scenarios
- **Rate Limiting**: Implement request rate limiting
- **Queue System**: Add job queue for heavy processing
- **Caching Layer**: Implement Redis for frequent queries
- **CDN**: Use CDN for static assets and API responses

### Multi-Language Support
- Extend news sources for other countries
- Implement language-specific LLM models
- Add translation capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for classes and methods
- Write tests for new functionality

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For LLM orchestration framework
- **Supabase**: For vector database infrastructure
- **Vercel**: For serverless deployment platform
- **Google**: For Gemini AI capabilities
- **Swedish News Outlets**: For providing RSS feeds and content

---

**🚀 Ready to deploy?** Follow the setup instructions above and start monitoring Swedish news with AI-powered political bias analysis! 