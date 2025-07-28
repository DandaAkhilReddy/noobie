"""
NOOBIE AI News Fetcher
=====================

Advanced news aggregation system with multiple sources, fallbacks,
rate limiting, and intelligent content filtering.
"""

import requests
import feedparser
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlencode
import json

from .logger import get_logger, LogOperation
from .config import NoobieConfig

@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    summary: str
    url: str
    published_date: str
    source: str
    category: str
    content: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    sentiment_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary"""
        return {
            'title': self.title,
            'summary': self.summary,
            'url': self.url,
            'published_date': self.published_date,
            'source': self.source,
            'category': self.category,
            'content': self.content,
            'author': self.author,
            'image_url': self.image_url,
            'sentiment_score': self.sentiment_score
        }

class NewsFetcher:
    """
    Advanced news fetcher with multiple sources and intelligent aggregation
    """
    
    def __init__(self, config: NoobieConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NOOBIE-AI/1.0 (News Aggregator; akhil@hhamedicine.com)'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
        # API endpoints
        self.gnews_base_url = "https://gnews.io/api/v4/search"
        self.newsapi_base_url = "https://newsapi.org/v2/everything"
    
    def _rate_limit(self) -> None:
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request_with_retry(self, url: str, params: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic and exponential backoff"""
        
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                
                self.logger.debug(f"📡 Making request to: {url}", extra_data={
                    'url': url,
                    'params': params,
                    'attempt': attempt + 1
                })
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                self.logger.warning(f"🔄 Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    self.logger.info(f"⏳ Waiting {wait_time:.2f}s before retry...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"❌ All retry attempts failed for: {url}")
                    
        return None
    
    def fetch_gnews(self, query: str, max_results: int = 10) -> List[NewsArticle]:
        """Fetch news from GNews API"""
        
        if not self.config.news_api_key:
            self.logger.warning("🔑 GNews API key not configured")
            return []
        
        with LogOperation(f"GNews fetch: {query}", self.logger):
            params = {
                'q': query,
                'lang': 'en',
                'country': 'us',
                'max': min(max_results, 10),  # GNews limit
                'apikey': self.config.news_api_key
            }
            
            data = self._make_request_with_retry(self.gnews_base_url, params)
            
            if not data or 'articles' not in data:
                self.logger.warning(f"🚫 No articles found for query: {query}")
                return []
            
            articles = []
            for article_data in data['articles'][:max_results]:
                try:
                    article = NewsArticle(
                        title=article_data.get('title', ''),
                        summary=article_data.get('description', ''),
                        url=article_data.get('url', ''),
                        published_date=article_data.get('publishedAt', ''),
                        source=article_data.get('source', {}).get('name', 'Unknown'),
                        category=query,
                        content=article_data.get('content'),
                        author=article_data.get('author'),
                        image_url=article_data.get('image')
                    )
                    
                    if article.title and article.summary:
                        articles.append(article)
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Error parsing article: {e}")
                    continue
            
            self.logger.info(f"✅ Fetched {len(articles)} articles from GNews for: {query}")
            return articles
    
    def fetch_rss_feed(self, feed_url: str, category: str, max_results: int = 10) -> List[NewsArticle]:
        """Fetch news from RSS feed"""
        
        with LogOperation(f"RSS fetch: {feed_url}", self.logger):
            try:
                self._rate_limit()
                
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    self.logger.warning(f"⚠️ RSS feed parsing issues: {feed_url}")
                
                articles = []
                for entry in feed.entries[:max_results]:
                    try:
                        # Parse publication date
                        pub_date = entry.get('published', '')
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6]).isoformat()
                        
                        article = NewsArticle(
                            title=entry.get('title', ''),
                            summary=entry.get('summary', entry.get('description', '')),
                            url=entry.get('link', ''),
                            published_date=pub_date,
                            source=feed.feed.get('title', 'RSS Feed'),
                            category=category,
                            author=entry.get('author')
                        )
                        
                        if article.title and article.summary:
                            articles.append(article)
                            
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error parsing RSS entry: {e}")
                        continue
                
                self.logger.info(f"✅ Fetched {len(articles)} articles from RSS: {category}")
                return articles
                
            except Exception as e:
                self.logger.error(f"❌ Error fetching RSS feed {feed_url}: {e}")
                return []
    
    def fetch_google_news_rss(self, query: str, max_results: int = 10) -> List[NewsArticle]:
        """Fetch news from Google News RSS (no API key required)"""
        
        # Encode query for URL
        encoded_query = urlencode({'q': query})
        rss_url = f"https://news.google.com/rss/search?{encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        return self.fetch_rss_feed(rss_url, query, max_results)
    
    def generate_mock_articles(self, category: str, count: int = 5) -> List[NewsArticle]:
        """Generate mock articles for testing"""
        
        if not self.config.mock_mode:
            return []
        
        self.logger.info(f"🎭 Generating {count} mock articles for: {category}")
        
        mock_templates = [
            {
                'title': f'Breaking: Major Development in {category.title()}',
                'summary': f'Recent developments in {category} show significant changes that could impact global markets and policy decisions.',
                'source': 'Mock News Network'
            },
            {
                'title': f'{category.title()} Trends Show Positive Growth',
                'summary': f'Analysis of current {category} trends indicates sustained growth and positive outlook for the coming months.',
                'source': 'Global Analysis Today'
            },
            {
                'title': f'Expert Commentary on {category.title()} Developments',
                'summary': f'Leading experts weigh in on recent {category} developments and their potential implications.',
                'source': 'Expert Insights'
            }
        ]
        
        articles = []
        for i in range(min(count, len(mock_templates))):
            template = mock_templates[i]
            
            article = NewsArticle(
                title=template['title'],
                summary=template['summary'],
                url=f"https://mock-news.com/article-{i+1}",
                published_date=datetime.now().isoformat(),
                source=template['source'],
                category=category,
                content=f"Full content for {template['title']}..."
            )
            
            articles.append(article)
        
        return articles
    
    def fetch_trending_news(self) -> List[NewsArticle]:
        """Fetch trending news from all configured sources"""
        
        with LogOperation("Fetch trending news", self.logger):
            all_articles = []
            
            # Fetch from each configured category
            for category in self.config.news_categories:
                category_articles = []
                
                # Try GNews first
                if self.config.news_api_key:
                    gnews_articles = self.fetch_gnews(category, max_results=3)
                    category_articles.extend(gnews_articles)
                
                # Fallback to Google News RSS if needed
                if len(category_articles) < 2:
                    rss_articles = self.fetch_google_news_rss(category, max_results=3)
                    category_articles.extend(rss_articles)
                
                # Use mock articles if still not enough and mock mode enabled
                if len(category_articles) < 1 and self.config.mock_mode:
                    mock_articles = self.generate_mock_articles(category, count=2)
                    category_articles.extend(mock_articles)
                
                all_articles.extend(category_articles)
            
            # Remove duplicates based on title similarity
            unique_articles = self._deduplicate_articles(all_articles)
            
            # Limit to max articles
            final_articles = unique_articles[:self.config.max_articles]
            
            self.logger.info(f"📰 Total articles fetched: {len(final_articles)}", extra_data={
                'total_fetched': len(all_articles),
                'after_deduplication': len(unique_articles),
                'final_count': len(final_articles),
                'categories': self.config.news_categories
            })
            
            return final_articles
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Simple deduplication based on title
            title_words = set(article.title.lower().split())
            
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                
                # If 70% of words match, consider it a duplicate
                if len(title_words & seen_words) / len(title_words | seen_words) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(article.title.lower())
        
        removed_count = len(articles) - len(unique_articles)
        if removed_count > 0:
            self.logger.info(f"🔄 Removed {removed_count} duplicate articles")
        
        return unique_articles
    
    def save_articles_cache(self, articles: List[NewsArticle], cache_file: str = None) -> str:
        """Save articles to cache file"""
        
        if not cache_file:
            cache_file = f"news_cache_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'count': len(articles),
            'articles': [article.to_dict() for article in articles]
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Articles cached to: {cache_file}")
        return cache_file
    
    def load_articles_cache(self, cache_file: str) -> List[NewsArticle]:
        """Load articles from cache file"""
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            articles = []
            for article_data in cache_data.get('articles', []):
                article = NewsArticle(**article_data)
                articles.append(article)
            
            self.logger.info(f"📂 Loaded {len(articles)} articles from cache: {cache_file}")
            return articles
            
        except Exception as e:
            self.logger.error(f"❌ Error loading cache file {cache_file}: {e}")
            return []