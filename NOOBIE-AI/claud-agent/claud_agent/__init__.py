"""
NOOBIE AI - Intelligent Blog Generation System
==============================================

A production-grade AI system that automatically generates daily blog posts
from trending world news using advanced language models.

Features:
- Multi-source news aggregation
- Claude AI-powered content generation
- Automated GitHub Pages publishing
- Azure Functions cloud deployment
- Comprehensive error handling and logging

Author: Akhil Reddy
Repository: https://github.com/akhilreddydanda/NOOBIE
"""

__version__ = "1.0.0"
__author__ = "Akhil Reddy"
__email__ = "akhil@hhamedicine.com"
__description__ = "NOOBIE AI - Intelligent automated blog generation system"
__url__ = "https://github.com/akhilreddydanda/NOOBIE"

# Core imports
from .news_fetcher import NewsFetcher, NewsArticle
from .blog_writer import BlogWriter, BlogPost
from .github_publisher import GitHubPublisher, PublishResult
from .orchestrator import NoobieOrchestrator
from .config import NoobieConfig
from .logger import get_logger, setup_logging

# Export main classes
__all__ = [
    'NewsFetcher',
    'NewsArticle',
    'BlogWriter', 
    'BlogPost',
    'GitHubPublisher',
    'PublishResult',
    'NoobieOrchestrator',
    'NoobieConfig',
    'get_logger',
    'setup_logging'
]

# Package metadata
PACKAGE_INFO = {
    'name': 'noobie-ai',
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'url': __url__,
    'license': 'MIT',
    'python_requires': '>=3.8',
    'keywords': ['ai', 'blog', 'automation', 'news', 'claude', 'azure'],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ]
}