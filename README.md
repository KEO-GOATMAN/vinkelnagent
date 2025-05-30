# 🤖 Automated Politically-Aware News Summarization & Publishing Agent

> An intelligent, fully automated news agent that monitors Swedish news sources, analyzes political bias, generates neutral summaries using RAG-enhanced LLMs, and publishes to WordPress - all deployed on Vercel.

## ✨ Features

### 🎯 Core Functionality
- **Automated News Monitoring**: Continuous RSS feed monitoring of Swedish news sources
- **Political Bias Analysis**: Categorizes sources as Left, Center, or Right
- **Bias-Specific Summaries**: Generates "what the Left/Center/Right is saying" perspectives
- **Neutral AI Summarization**: RAG-enhanced neutral summaries using Google Gemini
- **WordPress Publishing**: Automated posting with internal linking
- **Modern Frontend**: React-based interface with political bias visualization

### 🧠 AI & Machine Learning
- **Large Language Models**: Google Gemini via LangChain
- **Retrieval-Augmented Generation (RAG)**: Historical context for better summaries
- **Vector Database**: Supabase with pg_vector for semantic search
- **Embeddings**: Sentence transformers for content similarity

### 🌐 Architecture
- **Serverless Deployment**: Vercel Functions for scalability
- **Cron Jobs**: Automated RSS monitoring every hour
- **Modern Frontend**: React with TypeScript and Tailwind CSS
- **RESTful API**: Clean endpoint design for integration

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/news-agent.git
cd news-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create `.env` file:
```bash
# Core API Keys
GEMINI_API_KEY=your_google_gemini_api_key
SERPER_API_KEY=your_serper_search_api_key

# Supabase Vector Database
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# WordPress Integration
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your_wp_username
WORDPRESS_PASSWORD=your_wp_app_password
```

### 3. Database Setup
The Supabase tables are automatically configured. Vector extension and indexes are included.

### 4. Test Locally
```bash
# Run quick functionality test
python quick_test.py

# Test individual components
python basic_component_test.py

# Full workflow test
python real_workflow_test.py
```

### 5. Deploy to Vercel
```bash
# Deploy using Vercel CLI
npx vercel login
npx vercel

# Or use GitHub integration via Vercel dashboard
```

## 📁 Project Structure

```
├── api/                          # Vercel serverless functions
│   ├── process_news_topic.py     # Main news processing endpoint
│   ├── rss_monitor.py            # Automated RSS monitoring
│   └── health.py                 # Health check endpoint
├── src/
│   ├── components/               # Core business logic
│   │   ├── llm_manager.py        # LLM integration & prompt management
│   │   ├── vector_store.py       # RAG and vector database
│   │   └── wordpress_client.py   # WordPress API integration
│   ├── utils/                    # Utility functions
│   │   ├── web_scraper.py        # News article extraction
│   │   └── rss_parser.py         # RSS feed processing
│   ├── config/
│   │   └── settings.py           # Configuration management
│   └── models/
│       └── data_models.py        # Pydantic data models
├── public/                       # React frontend
│   ├── index.html
│   ├── script.js                 # Main frontend logic
│   └── style.css                 # Tailwind CSS styling
├── tests/                        # Test suite
│   ├── basic_component_test.py   # Component validation
│   ├── quick_test.py             # Quick functionality check
│   └── real_workflow_test.py     # End-to-end workflow test
├── vercel.json                   # Vercel configuration & cron jobs
├── requirements.txt              # Python dependencies
└── DEPLOYMENT_GUIDE.md          # Detailed deployment instructions
```

## 🔧 API Endpoints

### Main Processing
```http
POST /api/process_news_topic
Content-Type: application/json

{
  "topic": "Swedish Elections 2024",
  "description": "Latest political developments",
  "url": "https://example.com/article" // optional
}
```

**Response:**
```json
{
  "success": true,
  "neutral_summary": "Comprehensive neutral analysis...",
  "bias_summaries": {
    "Left": "Left-leaning perspective...",
    "Center": "Centrist viewpoint...",
    "Right": "Right-leaning analysis..."
  },
  "sources": [
    {"name": "Source A", "bias": "Left", "url": "..."},
    {"name": "Source B", "bias": "Center", "url": "..."}
  ],
  "wordpress_post_id": 123
}
```

### RSS Monitoring (Automated)
```http
GET /api/rss_monitor
```
Triggers automatically every hour via Vercel Cron

### Health Check
```http
GET /api/health
```

## 🎨 Frontend Features

- **Clean, Modern UI**: Responsive design with Tailwind CSS
- **Political Bias Visualization**: Interactive bar chart showing source distribution
- **Real-time Processing**: Live updates during news analysis
- **Mobile Responsive**: Optimized for all device sizes
- **Accessibility**: WCAG compliant design

## 🔍 Swedish News Sources

The agent monitors these hardcoded Swedish news outlets:

**Left-leaning:**
- Aftonbladet
- Expressen (some content)
- ETC

**Center:**
- SVT Nyheter
- SR Ekot
- TT Nyhetsbyrån

**Right-leaning:**
- Svenska Dagbladet
- Dagens Nyheter (some content)
- Dagens Industri

## 🧪 Testing

### Component Tests
```bash
# Test individual components
python basic_component_test.py
```

### Quick Functionality Check
```bash
# Verify core setup
python quick_test.py
```

### Full Workflow Test
```bash
# End-to-end processing test
python real_workflow_test.py
```

## 📊 Performance & Scalability

- **Serverless Architecture**: Auto-scaling Vercel Functions
- **Vector Database**: Optimized similarity search with indexes
- **Efficient LLM Usage**: Context-aware prompt management
- **Caching**: Built-in caching for static assets and API responses
- **Error Handling**: Robust error recovery and logging

## 🔐 Security

- **Environment Variables**: Secure credential management
- **API Key Rotation**: Support for key updates without downtime
- **Input Validation**: Pydantic models for request validation
- **Rate Limiting**: Built-in Vercel function limits
- **HTTPS**: Secure communication for all endpoints

## 🚀 Deployment Options

### Option 1: Vercel CLI
```bash
npx vercel login
npx vercel --prod
```

### Option 2: GitHub Integration
1. Push to GitHub
2. Connect repository to Vercel
3. Configure environment variables
4. Auto-deploy on push

### Option 3: Manual Deployment
Upload via Vercel dashboard with manual configuration

## 📈 Monitoring & Observability

- **Vercel Analytics**: Function performance and usage
- **Supabase Monitoring**: Database queries and vector operations
- **Error Tracking**: Comprehensive logging for debugging
- **Health Checks**: Automated system status verification

## 🔄 Maintenance

### Regular Tasks
- Monitor API key usage and limits
- Review and update news source lists
- Check vector database performance
- Validate bias classifications
- Update dependency versions

### Automated Tasks
- RSS feed monitoring (hourly)
- Database cleanup (weekly)
- Health checks (continuous)
- Error reporting (real-time)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `python -m pytest tests/`
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/news-agent/issues)
- **Documentation**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **API Reference**: Check endpoint documentation above

---

**Built with:** Python 3.13, LangChain, Google Gemini, Supabase, Vercel, React

**Last Updated:** January 2025 