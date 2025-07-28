# NOOBIE AI - Automated Blog Generation System

## 🤖 Overview

NOOBIE AI is a comprehensive, production-ready artificial intelligence system that automatically generates and publishes daily blog posts based on global news analysis. Built with enterprise-grade engineering standards, it combines multiple AI APIs, news sources, and automated publishing to create thoughtful, engaging content.

## ✨ Key Features

- **🔍 Multi-Source News Aggregation**: Fetches from GNews API, RSS feeds, and Google News
- **🤖 AI-Powered Content Generation**: Uses Claude and OpenAI APIs for intelligent blog writing
- **📤 Automated GitHub Pages Publishing**: Direct publishing with Jekyll optimization
- **⏰ Scheduled Automation**: Daily blog generation at 8:00 AM UTC via Azure Functions
- **🎛️ Manual Trigger Support**: HTTP endpoints for on-demand generation
- **📊 Production Logging**: Structured JSON logging with Azure Application Insights
- **🛡️ Robust Error Handling**: Retry logic, fallbacks, and comprehensive monitoring
- **🎭 Mock Mode**: Testing capabilities with generated content

## 🏗️ Architecture

```
claud-agent/
├── claud_agent/           # Core Python package
│   ├── config.py          # Configuration management
│   ├── logger.py          # Advanced logging system
│   ├── news_fetcher.py    # Multi-source news aggregation
│   ├── blog_writer.py     # AI-powered content generation
│   └── github_publisher.py # GitHub Pages publishing
├── azure_function/        # Serverless automation
│   ├── function_app.py    # Azure Functions entry points
│   ├── requirements.txt   # Dependencies
│   ├── host.json         # Function configuration
│   └── local.settings.json # Development settings
├── tests/                 # Comprehensive test suite
├── docs/                  # Documentation
└── deploy_azure.sh       # Deployment automation
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with pip
2. **Azure Account** with Functions support
3. **GitHub Account** with repository access
4. **API Keys**:
   - GNews API key ([gnews.io](https://gnews.io))
   - Claude API key ([anthropic.com](https://anthropic.com))
   - OpenAI API key ([openai.com](https://openai.com)) (optional)
   - GitHub Personal Access Token

### Local Development

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/akhilreddydanda/NOOBIE.git
   cd NOOBIE/claud-agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r azure_function/requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   # Copy and edit local settings
   cp azure_function/local.settings.json.example azure_function/local.settings.json
   
   # Add your API keys
   export NEWS_API_KEY="your_gnews_api_key"
   export CLAUDE_API_KEY="your_claude_api_key" 
   export GITHUB_TOKEN="your_github_token"
   export GITHUB_REPO="username/repository"
   ```

3. **Test Locally**:
   ```bash
   cd azure_function
   func start --python
   
   # Test endpoints
   curl http://localhost:7071/api/health
   curl -X POST http://localhost:7071/api/manual_generate
   ```

### Azure Deployment

1. **Automated Deployment**:
   ```bash
   chmod +x deploy_azure.sh
   ./deploy_azure.sh
   ```

2. **Configure Application Settings**:
   The deployment script automatically sets up:
   - Resource group and storage account
   - Function App with Python runtime
   - Application Insights for monitoring
   - Required environment variables

3. **Verify Deployment**:
   ```bash
   # Check function status
   curl https://your-function-app.azurewebsites.net/api/health
   
   # View logs
   az functionapp logs tail --name your-function-app --resource-group noobie-ai-rg
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEWS_API_KEY` | Yes | GNews.io API key for news fetching |
| `CLAUDE_API_KEY` | Yes* | Anthropic Claude API key |
| `OPENAI_API_KEY` | Yes* | OpenAI API key (if Claude not available) |
| `GITHUB_TOKEN` | Yes | GitHub PAT with repo access |
| `GITHUB_REPO` | Yes | Target repository (username/repo) |
| `GITHUB_BRANCH` | No | Target branch (default: main) |
| `BLOG_TITLE` | No | Blog title for Jekyll |
| `AUTHOR_NAME` | No | Author name for posts |
| `MAX_ARTICLES` | No | Max articles to process (default: 8) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
| `MOCK_MODE` | No | Enable mock content for testing |

*At least one AI API key (Claude or OpenAI) is required

### Configuration File

Create `config.json` for persistent settings:

```json
{
  "blog_title": "NOOBIE AI - Daily News Intelligence",
  "blog_description": "AI-powered daily analysis of global news and trends",
  "author_name": "NOOBIE AI",
  "github_repo": "akhilreddydanda/NOOBIE",
  "max_articles": 8,
  "news_categories": [
    "global politics",
    "technology trends",
    "economic developments",
    "international affairs",
    "breaking news"
  ]
}
```

## 📝 Usage

### Scheduled Execution

The system automatically runs daily at 8:00 AM UTC:

1. **Fetches** trending news from configured sources
2. **Analyzes** articles using AI for key themes
3. **Generates** comprehensive blog post (800-1500 words)
4. **Publishes** to GitHub Pages with Jekyll optimization
5. **Logs** execution statistics and performance metrics

### Manual Execution

Trigger blog generation manually via HTTP API:

```bash
# Basic manual generation
curl -X POST https://your-function-app.azurewebsites.net/api/manual_generate \
  -H "Content-Type: application/json" \
  -d '{}'

# With custom parameters
curl -X POST https://your-function-app.azurewebsites.net/api/manual_generate \
  -H "Content-Type: application/json" \
  -d '{
    "mock_mode": false,
    "max_articles": 10
  }'
```

### Monitoring and Health Checks

```bash
# Health check (anonymous access)
curl https://your-function-app.azurewebsites.net/api/health

# Detailed status (requires function key)
curl https://your-function-app.azurewebsites.net/api/status?code=your_function_key

# View recent posts
curl https://your-function-app.azurewebsites.net/api/status?code=your_function_key | jq '.recent_posts'
```

## 🧪 Testing

### Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=claud_agent --cov-report=html
```

### Integration Tests

```bash
# Test news fetching
python -m claud_agent.news_fetcher

# Test blog generation
python -m claud_agent.blog_writer

# Test GitHub publishing (requires valid tokens)
python -m claud_agent.github_publisher
```

### Mock Mode Testing

```bash
# Enable mock mode for testing without API calls
export MOCK_MODE=true
python -c "
from claud_agent.config import load_config
from claud_agent.news_fetcher import NewsFetcher
config = load_config()
config.mock_mode = True
fetcher = NewsFetcher(config)
articles = fetcher.generate_mock_articles('technology', 3)
print(f'Generated {len(articles)} mock articles')
"
```

## 📊 Monitoring and Observability

### Logging

- **Console Output**: Colored, emoji-enhanced logs for development
- **File Logging**: Structured JSON logs with rotation
- **Azure Application Insights**: Production telemetry and monitoring

### Key Metrics

- Articles fetched per execution
- Blog generation success rate
- Publishing success rate  
- Average execution time
- API response times
- Error rates by component

### Alerting

Configure Azure Monitor alerts for:
- Function execution failures
- API quota exhaustion
- GitHub publishing failures
- High error rates

## 🔧 Advanced Configuration

### Custom News Sources

Add RSS feeds to expand news coverage:

```python
# In news_fetcher.py, add custom RSS sources
custom_feeds = [
    ('https://rss.cnn.com/rss/edition.rss', 'international'),
    ('https://feeds.bbci.co.uk/news/world/rss.xml', 'global'),
    ('https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', 'technology')
]

for feed_url, category in custom_feeds:
    articles.extend(self.fetch_rss_feed(feed_url, category))
```

### AI Model Customization

Customize content generation prompts:

```python
# Modify system prompt in blog_writer.py
custom_prompt = """
You are NOOBIE AI, specializing in [YOUR DOMAIN].
Your analysis should focus on [SPECIFIC ASPECTS].
Write in [YOUR PREFERRED STYLE].
"""
```

### GitHub Pages Themes

Customize Jekyll configuration:

```yaml
# In github_publisher.py, modify Jekyll config
theme: minimal-mistakes
plugins:
  - jekyll-sitemap
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-paginate-v2
```

## 🛠️ Development

### Code Structure

- **Modular Design**: Separate concerns for news, AI, and publishing
- **Type Safety**: Full type hints with mypy compatibility
- **Error Handling**: Comprehensive exception handling with recovery
- **Logging**: Structured logging with contextual information
- **Testing**: Unit and integration tests with mocking
- **Documentation**: Inline docstrings and external documentation

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Quality

```bash
# Format code
black claud_agent/ azure_function/ tests/

# Lint code
flake8 claud_agent/ azure_function/ tests/

# Type checking
mypy claud_agent/

# Security scanning
bandit -r claud_agent/
```

## 📋 Troubleshooting

### Common Issues

**1. API Key Issues**
```bash
# Verify environment variables
env | grep -E "(NEWS_API|CLAUDE_API|OPENAI_API|GITHUB_TOKEN)"

# Test API connectivity
curl -H "Authorization: Bearer $CLAUDE_API_KEY" https://api.anthropic.com/v1/messages
```

**2. GitHub Publishing Failures**
```bash
# Check repository permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/$GITHUB_REPO

# Verify GitHub Pages is enabled
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/$GITHUB_REPO/pages
```

**3. Azure Function Issues**
```bash
# View function logs
az functionapp logs tail --name your-function-app --resource-group noobie-ai-rg

# Check application settings
az functionapp config appsettings list --name your-function-app --resource-group noobie-ai-rg
```

**4. News Fetching Problems**
```bash
# Test GNews API
curl "https://gnews.io/api/v4/search?q=technology&token=$NEWS_API_KEY"

# Test Google News RSS fallback
curl "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en"
```

### Debug Mode

Enable detailed debugging:
```bash
export LOG_LEVEL=DEBUG
export MOCK_MODE=true  # For testing without API calls
```

## 📚 Resources

- **GNews API Documentation**: [gnews.io/docs](https://gnews.io/docs)
- **Claude API Reference**: [docs.anthropic.com](https://docs.anthropic.com)
- **OpenAI API Guide**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Azure Functions Python**: [docs.microsoft.com](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- **GitHub Pages Jekyll**: [jekyllrb.com](https://jekyllrb.com)

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/akhilreddydanda/NOOBIE/issues)
- **Discussions**: [GitHub Discussions](https://github.com/akhilreddydanda/NOOBIE/discussions)
- **Email**: [akhil@hhamedicine.com](mailto:akhil@hhamedicine.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] **Multi-language Support**: Support for non-English content generation
- [ ] **Advanced Analytics**: Detailed performance metrics and usage statistics  
- [ ] **Content Scheduling**: Advanced scheduling with timezone support
- [ ] **Social Media Integration**: Auto-posting to Twitter, LinkedIn
- [ ] **Email Newsletters**: Automated newsletter generation and distribution
- [ ] **Custom AI Models**: Fine-tuned models for domain-specific content
- [ ] **WordPress Integration**: Direct publishing to WordPress sites
- [ ] **SEO Optimization**: Advanced SEO analysis and optimization
- [ ] **Content Templates**: Customizable templates for different content types
- [ ] **Multi-tenant Support**: Support for multiple blogs from single deployment

---

**Built with ❤️ by the NOOBIE AI Team**

*Powered by Azure Functions • Enhanced by AI • Published to GitHub Pages*