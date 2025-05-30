# 🚀 Deployment Guide: Automated Politically-Aware News Summarization Agent

## Overview

This guide walks you through deploying your complete news agent to Vercel with GitHub integration for continuous deployment.

## 📋 Prerequisites

1. **GitHub Account**: For repository hosting and CI/CD
2. **Vercel Account**: Connected to your GitHub account
3. **Supabase Project**: Already set up with vector database
4. **API Keys**: All required API keys ready

## 🔑 Required Environment Variables

Set these in your Vercel project settings:

### Core API Keys
```bash
GEMINI_API_KEY=your_google_gemini_api_key_here
SERPER_API_KEY=your_serper_search_api_key_here
```

### Supabase Configuration
```bash
SUPABASE_URL=https://wwrchbrslghkgozqunmm.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### WordPress Integration
```bash
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your_wp_username
WORDPRESS_PASSWORD=your_wp_app_password
```

## 🌐 Step-by-Step Deployment

### 1. Push to GitHub

```bash
# Add GitHub remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/news-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install and login to Vercel
npx vercel login

# Deploy (follow prompts)
npx vercel

# Deploy to production
npx vercel --prod
```

#### Option B: Using Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure environment variables
5. Deploy

### 3. Configure Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to "Settings" → "Environment Variables"
3. Add all the required variables listed above
4. Redeploy the project

## 🔍 API Endpoints

Once deployed, your agent will have these endpoints:

### Main Processing Endpoint
```
POST https://your-app.vercel.app/api/process_news_topic

Body:
{
  "topic": "Swedish Elections 2024",
  "description": "Latest developments in Swedish politics"
}
```

### RSS Monitor (Cron Job)
```
GET https://your-app.vercel.app/api/rss_monitor
```
Automatically triggered every hour by Vercel Cron

### Health Check
```
GET https://your-app.vercel.app/api/health
```

## 🎯 Testing Your Deployment

### 1. Test the Health Endpoint
```bash
curl https://your-app.vercel.app/api/health
```

### 2. Test News Processing
```bash
curl -X POST https://your-app.vercel.app/api/process_news_topic \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Swedish Elections 2024",
    "description": "Test news topic for deployment verification"
  }'
```

### 3. Check Frontend
Visit `https://your-app.vercel.app` to see the React frontend

## 📊 Monitoring and Logs

### Vercel Dashboard
- Monitor function invocations
- Check error logs
- View performance metrics

### Supabase Dashboard
- Monitor database queries
- Check vector store usage
- View stored embeddings

## 🔧 Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   - Verify all variables in Vercel settings
   - Redeploy after adding variables

2. **Supabase Connection Errors**
   - Check Supabase URL and key
   - Verify vector extension is enabled

3. **Function Timeout**
   - Vercel free tier: 10s timeout
   - Consider upgrading for longer processing

4. **Import Errors**
   - Check `requirements.txt` is complete
   - Verify Python dependencies

### Debug Commands
```bash
# Check Vercel logs
npx vercel logs

# Redeploy with verbose output
npx vercel --debug
```

## 🚦 Production Checklist

- [ ] All environment variables configured
- [ ] Supabase database tables created
- [ ] WordPress site accessible
- [ ] API keys valid and active
- [ ] Cron job configured (every hour)
- [ ] Frontend loads correctly
- [ ] Health check responds
- [ ] News processing works end-to-end

## 📈 Performance Optimization

1. **Function Cold Starts**: Vercel automatically optimizes
2. **Database Queries**: Indexed for performance
3. **LLM Calls**: Efficient prompt management
4. **Caching**: Built-in for static assets

## 🔄 Continuous Deployment

Every push to your `main` branch will automatically:
1. Build the application
2. Run any tests
3. Deploy to production
4. Update the live site

## 🆘 Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Supabase Documentation**: [supabase.com/docs](https://supabase.com/docs)
- **LangChain Documentation**: [langchain.com](https://langchain.com)

---

Your automated news agent is now ready for production! 🎉 