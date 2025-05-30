# 🤖 Automated Politically-Aware News Summarization & Publishing Agent

> An intelligent, fully automated news agent that monitors Swedish news sources, analyzes political bias, generates neutral summaries using RAG-enhanced LLMs, and publishes to WordPress - deployed on Vercel.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/KEO-GOATMAN/vinkelnagent)

## ✨ Features

### 🎯 Core Functionality
- **Automated News Monitoring**: Continuous RSS feed monitoring of Swedish news sources
- **Political Bias Analysis**: Categorizes sources as Left, Center, or Right
- **Bias-Specific Summaries**: Generates "what the Left/Center/Right is saying" perspectives
- **Neutral AI Summarization**: RAG-enhanced neutral summaries using Google Gemini
- **WordPress Publishing**: Automated posting with internal linking
- **Vector Search**: Historical context retrieval for enhanced content generation

### 🧠 AI & Machine Learning
- **Large Language Models**: Google Gemini via LangChain
- **Retrieval-Augmented Generation (RAG)**: Historical context for better summaries
- **Vector Database**: Supabase with pg_vector for semantic search
- **Embeddings**: Sentence transformers for content similarity

### 🌐 Architecture
- **Serverless Deployment**: Vercel Functions for scalability
- **Cron Jobs**: Automated RSS monitoring via Vercel Cron
- **RESTful API**: Clean endpoint design for integration
- **Modern Stack**: Python, LangChain, Supabase, Vercel

## 🚀 Quick Deploy to Vercel

### 1. One-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/KEO-GOATMAN/vinkelnagent)

### 2. Environment Variables
Add these in your Vercel dashboard:

```bash
# Required API Keys
GEMINI_API_KEY=your_google_gemini_api_key
SERPER_API_KEY=your_serper_search_api_key

# Supabase Vector Database
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# WordPress Integration (Optional)
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your_wp_username
WORDPRESS_PASSWORD=your_wp_app_password
```

### 3. Setup Supabase
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Enable the `vector` extension in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. The `news_articles` table will be automatically created on first use

## 📁 Project Structure

```
├── api/                          # Vercel serverless functions
│   ├── process_news_topic.py     # Main news processing endpoint
│   ├── rss_monitor.py            # Automated RSS monitoring (cron)
│   └── health.py                 # Health check endpoint
├── src/
│   ├── components/               # Core business logic
│   │   ├── llm_manager.py        # LLM integration & prompt management
│   │   └── wordpress_client.py   # WordPress API integration
│   ├── vectorstores/
│   │   └── supabase_store.py     # Vector database & RAG
│   ├── utils/
│   │   ├── web_scraper.py        # News article extraction
│   │   └── rss_parser.py         # RSS feed processing
│   ├── config/
│   │   └── settings.py           # Configuration & Swedish news sources
│   └── models/
│       └── data_models.py        # Pydantic data models
├── vercel.json                   # Vercel config with cron jobs
├── requirements.txt              # Python dependencies
├── DEPLOYMENT_GUIDE.md          # Detailed setup instructions
└── README.md                    # This file
```

## 🔧 API Endpoints

### Main Processing
```http
POST /api/process_news_topic
Content-Type: application/json

{
  "topic": "Swedish Elections 2024",
  "description": "Latest political developments",
  "url": "https://example.com/article"
}
```

**Response:**
```json
{
  "success": true,
  "neutral_summary": {
    "title": "Neutral Summary Title",
    "content": "Comprehensive neutral analysis...",
    "key_facts": ["Fact 1", "Fact 2"],
    "internal_links": [{"title": "Related Article", "url": "/article/123"}]
  },
  "bias_summaries": [
    {
      "bias": "Left",
      "summary": "Left-leaning perspective...",
      "source_count": 3
    }
  ],
  "bias_visualization": [
    {"source_name": "Aftonbladet", "bias": "Left", "url": "..."}
  ],
  "wordpress_post_id": 123,
  "processing_stats": {
    "articles_found": 8,
    "processing_time": "2.3s"
  }
}
```

### RSS Monitoring (Automated)
```http
GET /api/rss_monitor
```
- Runs automatically every hour via Vercel Cron
- Monitors all Swedish news RSS feeds
- Processes new articles automatically

### Health Check
```http
GET /api/health
```
- System status and component health
- Database connectivity check
- API availability verification

## 🔍 Swedish News Sources

The agent monitors these Swedish news outlets with political bias mapping:

### Left-leaning Sources
- **Aftonbladet** - Leading tabloid with left perspective
- **ETC** - Independent left-wing publication
- **Flamman** - Socialist publication

### Center Sources  
- **SVT Nyheter** - Public service broadcaster
- **SR Ekot** - Public radio news
- **TT Nyhetsbyrån** - National news agency

### Right-leaning Sources
- **Svenska Dagbladet** - Conservative daily newspaper
- **Dagens Industri** - Business and industry focus
- **Dagens Nyheter** - Liberal daily newspaper

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- Git
- Supabase account
- Google Cloud account (for Gemini API)
- Serper account (for web search)

### Setup
```bash
# Clone repository
git clone https://github.com/KEO-GOATMAN/vinkelnagent.git
cd vinkelnagent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env with your credentials
```

### Testing API Locally
```bash
# Start local development server
vercel dev

# Test endpoints
curl -X POST http://localhost:3000/api/process_news_topic \
  -H "Content-Type: application/json" \
  -d '{"topic": "Swedish Elections 2024"}'
```

## 🔐 Security & Privacy

- **API Key Protection**: All sensitive credentials stored as environment variables
- **Input Validation**: Comprehensive validation of all user inputs
- **Rate Limiting**: Built-in protection against abuse
- **Data Privacy**: No personal data stored; only public news content

## 📈 Performance

- **Cold Start**: ~2-3 seconds (Vercel serverless)
- **Processing Time**: 5-15 seconds per news topic
- **RSS Monitoring**: Processes 20+ sources in under 30 seconds
- **Vector Search**: Sub-second similarity queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup
- **Issues**: Report bugs via [GitHub Issues](https://github.com/KEO-GOATMAN/vinkelnagent/issues)
- **Discussions**: Join discussions in [GitHub Discussions](https://github.com/KEO-GOATMAN/vinkelnagent/discussions)

## 🚀 Roadmap

- [ ] Additional news sources (Norwegian, Danish)
- [ ] Real-time WebSocket updates
- [ ] Advanced bias detection algorithms
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Mobile app

---

**Built with ❤️ using LangChain, Vercel, and Supabase** 