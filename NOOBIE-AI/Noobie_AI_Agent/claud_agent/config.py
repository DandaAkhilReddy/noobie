"""
NOOBIE AI Configuration Management
=================================

Handles all configuration loading, validation, and environment management
for the NOOBIE AI system.
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

@dataclass
class NoobieConfig:
    """
    Configuration class for NOOBIE AI system
    """
    # API Keys
    news_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # GitHub Configuration
    github_token: Optional[str] = None
    github_repo: str = "akhilreddydanda/NOOBIE"
    github_branch: str = "main"
    
    # Blog Configuration
    blog_title: str = "NOOBIE AI - Daily News Intelligence"
    blog_description: str = "AI-powered daily analysis of global news and trends"
    author_name: str = "NOOBIE AI"
    
    # Processing Settings
    max_articles: int = 8
    min_article_length: int = 100
    max_blog_length: int = 3000
    
    # Logging
    log_level: str = "INFO"
    enable_console_logging: bool = True
    enable_file_logging: bool = True
    
    # Azure Settings
    function_timeout: int = 600  # 10 minutes
    retry_attempts: int = 3
    retry_delay: int = 5
    
    # Feature Flags
    upload_to_github: bool = True
    save_local_backup: bool = True
    enable_analytics: bool = True
    mock_mode: bool = False
    
    # News Categories
    news_categories: List[str] = field(default_factory=lambda: [
        "global politics",
        "technology trends", 
        "economic developments",
        "international affairs",
        "breaking news"
    ])
    
    @classmethod
    def from_env(cls) -> 'NoobieConfig':
        """Create configuration from environment variables"""
        return cls(
            # API Keys
            news_api_key=os.getenv('NEWS_API_KEY'),
            claude_api_key=os.getenv('CLAUDE_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            
            # GitHub
            github_token=os.getenv('GITHUB_TOKEN'),
            github_repo=os.getenv('GITHUB_REPO', 'akhilreddydanda/NOOBIE'),
            github_branch=os.getenv('GITHUB_BRANCH', 'main'),
            
            # Blog Settings
            blog_title=os.getenv('BLOG_TITLE', 'NOOBIE AI - Daily News Intelligence'),
            author_name=os.getenv('AUTHOR_NAME', 'NOOBIE AI'),
            
            # Processing
            max_articles=int(os.getenv('MAX_ARTICLES', '8')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            
            # Features
            upload_to_github=os.getenv('UPLOAD_TO_GITHUB', 'true').lower() == 'true',
            mock_mode=os.getenv('MOCK_MODE', 'false').lower() == 'true',
            retry_attempts=int(os.getenv('RETRY_ATTEMPTS', '3')),
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'NoobieConfig':
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Check required API keys
        if not self.news_api_key:
            errors.append("NEWS_API_KEY is required")
        
        if not self.claude_api_key and not self.openai_api_key:
            errors.append("At least one AI API key (CLAUDE_API_KEY or OPENAI_API_KEY) is required")
        
        if self.upload_to_github and not self.github_token:
            errors.append("GITHUB_TOKEN is required when upload_to_github is enabled")
        
        # Validate ranges
        if self.max_articles < 1 or self.max_articles > 20:
            errors.append("max_articles must be between 1 and 20")
        
        if self.retry_attempts < 1 or self.retry_attempts > 10:
            errors.append("retry_attempts must be between 1 and 10")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding sensitive data)"""
        return {
            'github_repo': self.github_repo,
            'github_branch': self.github_branch,
            'blog_title': self.blog_title,
            'blog_description': self.blog_description,
            'author_name': self.author_name,
            'max_articles': self.max_articles,
            'log_level': self.log_level,
            'upload_to_github': self.upload_to_github,
            'mock_mode': self.mock_mode,
            'news_categories': self.news_categories,
            'has_news_api_key': bool(self.news_api_key),
            'has_claude_api_key': bool(self.claude_api_key),
            'has_github_token': bool(self.github_token),
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to JSON file (excluding sensitive data)"""
        config_dict = self.to_dict()
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

def load_config() -> NoobieConfig:
    """
    Load configuration with priority:
    1. Environment variables
    2. config.json file
    3. Default values
    """
    # Try to load from environment first
    config = NoobieConfig.from_env()
    
    # Check for config file
    config_file = Path('config.json')
    if config_file.exists():
        try:
            file_config = NoobieConfig.from_file(str(config_file))
            # Merge configurations (env takes priority)
            for field_name, field_def in config.__dataclass_fields__.items():
                env_value = getattr(config, field_name)
                file_value = getattr(file_config, field_name)
                
                # Use env value if set, otherwise use file value
                if env_value == field_def.default:
                    setattr(config, field_name, file_value)
                    
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
    
    return config

def create_sample_config() -> None:
    """Create a sample configuration file"""
    sample_config = {
        "blog_title": "NOOBIE AI - Daily News Intelligence",
        "blog_description": "AI-powered daily analysis of global news and trends",
        "author_name": "NOOBIE AI",
        "github_repo": "akhilreddydanda/NOOBIE",
        "github_branch": "main",
        "max_articles": 8,
        "log_level": "INFO",
        "upload_to_github": True,
        "mock_mode": False,
        "news_categories": [
            "global politics",
            "technology trends",
            "economic developments", 
            "international affairs",
            "breaking news"
        ]
    }
    
    with open('config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample config.json created. Please edit with your settings.")