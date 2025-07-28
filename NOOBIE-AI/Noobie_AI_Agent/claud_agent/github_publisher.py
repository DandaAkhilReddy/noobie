"""
NOOBIE AI GitHub Publisher
=========================

Advanced GitHub Pages publishing with automatic commit, push,
and Jekyll optimization for professional blog deployment.
"""

import requests
import base64
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

from .logger import get_logger, LogOperation
from .config import NoobieConfig
from .blog_writer import BlogPost

@dataclass
class PublishResult:
    """Result of publishing operation"""
    success: bool
    message: str
    url: Optional[str] = None
    commit_sha: Optional[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class GitHubPublisher:
    """
    Advanced GitHub Pages publisher with Jekyll optimization
    """
    
    def __init__(self, config: NoobieConfig):
        self.config = config
        self.logger = get_logger(__name__)
        
        # GitHub API settings
        self.api_base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if config.github_token:
            self.session.headers.update({
                "Authorization": f"token {config.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "NOOBIE-AI/1.0"
            })
    
    def _make_api_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make authenticated GitHub API request"""
        
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ GitHub API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
            return None
    
    def _get_file_content(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get existing file content from repository"""
        
        endpoint = f"/repos/{self.config.github_repo}/contents/{file_path}"
        
        self.logger.debug(f"Getting file content: {file_path}")
        
        response = self._make_api_request('GET', endpoint)
        return response
    
    def _create_or_update_file(self, file_path: str, content: str, message: str, sha: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create or update file in repository"""
        
        endpoint = f"/repos/{self.config.github_repo}/contents/{file_path}"
        
        # Encode content to base64
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": message,
            "content": content_encoded,
            "branch": self.config.github_branch
        }
        
        # Add SHA if updating existing file
        if sha:
            data["sha"] = sha
        
        self.logger.debug(f"{'Updating' if sha else 'Creating'} file: {file_path}")
        
        return self._make_api_request('PUT', endpoint, data)
    
    def _generate_jekyll_frontmatter(self, blog_post: BlogPost) -> str:
        """Generate Jekyll-compatible frontmatter"""
        
        frontmatter = f"""---
layout: post
title: "{blog_post.title.replace('"', '\\"')}"
date: {blog_post.publication_date}
author: "{blog_post.author}"
categories: [{blog_post.category}]
tags: [{', '.join(f'"{tag}"' for tag in blog_post.tags)}]
excerpt: "{blog_post.summary.replace('"', '\\"')[:200]}..."
seo:
  title: "{blog_post.seo_title or blog_post.title}"
  description: "{blog_post.seo_description or blog_post.summary[:155]}"
  type: article
word_count: {blog_post.word_count}
reading_time: {max(1, blog_post.word_count // 200)}
published: true
featured: false
comments: true
---

"""
        return frontmatter
    
    def _create_post_filename(self, blog_post: BlogPost) -> str:
        """Create Jekyll-compatible post filename"""
        
        # Extract date from publication_date
        pub_date = datetime.fromisoformat(blog_post.publication_date.replace('Z', '+00:00'))
        date_str = pub_date.strftime("%Y-%m-%d")
        
        # Create slug from title
        import re
        slug = re.sub(r'[^\w\s-]', '', blog_post.title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)[:50].strip('-')
        
        return f"_posts/{date_str}-{slug}.md"
    
    def publish_blog_post(self, blog_post: BlogPost) -> PublishResult:
        """Publish blog post to GitHub Pages"""
        
        if not self.config.github_token:
            return PublishResult(
                success=False,
                message="GitHub token not configured",
                errors=["GITHUB_TOKEN environment variable is required"]
            )
        
        with LogOperation(f"Publish blog post: {blog_post.title}", self.logger):
            
            try:
                # Generate Jekyll-compatible content
                frontmatter = self._generate_jekyll_frontmatter(blog_post)
                full_content = frontmatter + blog_post.content
                
                # Create filename
                filename = self._create_post_filename(blog_post)
                
                # Check if file already exists
                existing_file = self._get_file_content(filename)
                sha = existing_file.get('sha') if existing_file else None
                
                # Create commit message
                action = "Update" if sha else "Add"
                commit_message = f"{action} blog post: {blog_post.title}\n\nGenerated by NOOBIE AI\nTimestamp: {datetime.now().isoformat()}\nWord count: {blog_post.word_count}"
                
                # Upload file
                result = self._create_or_update_file(filename, full_content, commit_message, sha)
                
                if result:
                    # Generate URLs
                    repo_url = f"https://github.com/{self.config.github_repo}/blob/{self.config.github_branch}/{filename}"
                    pages_url = self._generate_pages_url(blog_post)
                    
                    self.logger.info(f"✅ Blog post published successfully", extra_data={
                        'filename': filename,
                        'commit_sha': result.get('commit', {}).get('sha'),
                        'repo_url': repo_url,
                        'pages_url': pages_url
                    })
                    
                    return PublishResult(
                        success=True,
                        message=f"Successfully published: {blog_post.title}",
                        url=pages_url,
                        commit_sha=result.get('commit', {}).get('sha')
                    )
                else:
                    return PublishResult(
                        success=False,
                        message="Failed to upload file to GitHub",
                        errors=["GitHub API request failed"]
                    )
                    
            except Exception as e:
                self.logger.error(f"❌ Error publishing blog post: {e}")
                return PublishResult(
                    success=False,
                    message=f"Publishing failed: {str(e)}",
                    errors=[str(e)]
                )
    
    def _generate_pages_url(self, blog_post: BlogPost) -> str:
        """Generate GitHub Pages URL for the blog post"""
        
        # Extract date from publication_date
        pub_date = datetime.fromisoformat(blog_post.publication_date.replace('Z', '+00:00'))
        
        # Create slug from title
        import re
        slug = re.sub(r'[^\w\s-]', '', blog_post.title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)[:50].strip('-')
        
        # Standard GitHub Pages URL structure
        username = self.config.github_repo.split('/')[0]
        repo_name = self.config.github_repo.split('/')[1]
        
        # Check if it's a user/organization page or project page
        if repo_name.lower() == f"{username.lower()}.github.io":
            # User/organization page
            base_url = f"https://{username.lower()}.github.io"
        else:
            # Project page
            base_url = f"https://{username.lower()}.github.io/{repo_name}"
        
        url_path = f"/{pub_date.year:04d}/{pub_date.month:02d}/{pub_date.day:02d}/{slug}/"
        
        return base_url + url_path
    
    def setup_jekyll_config(self) -> PublishResult:
        """Setup Jekyll configuration for the blog"""
        
        with LogOperation("Setup Jekyll configuration", self.logger):
            
            # Jekyll _config.yml content
            config_content = f"""# NOOBIE AI Blog Configuration
title: "{self.config.blog_title}"
description: "{self.config.blog_description}"
url: "https://{self.config.github_repo.split('/')[0].lower()}.github.io"
baseurl: ""

# Author information
author:
  name: "{self.config.author_name}"
  bio: "AI-powered daily news analysis and global insights"
  avatar: "/assets/images/noobie-avatar.png"

# Social links
github_username: {self.config.github_repo.split('/')[0]}

# Build settings
markdown: kramdown
highlighter: rouge
permalink: /:year/:month/:day/:title/

# Theme
theme: minima

# Plugins
plugins:
  - jekyll-feed
  - jekyll-sitemap
  - jekyll-seo-tag
  - jekyll-paginate

# Pagination
paginate: 10
paginate_path: "/page:num/"

# SEO
seo:
  title: "{self.config.blog_title}"
  description: "{self.config.blog_description}"
  keywords: "AI, blog, news, analysis, artificial intelligence, global news, automated blogging"

# Timezone
timezone: UTC

# Collections
collections:
  posts:
    output: true
    permalink: /:year/:month/:day/:title/

# Defaults
defaults:
  - scope:
      path: ""
      type: "posts"
    values:
      layout: "post"
      author: "{self.config.author_name}"
      show_excerpts: true

# Exclude
exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor/bundle/
  - vendor/cache/
  - vendor/gems/
  - vendor/ruby/
"""
            
            try:
                # Check if _config.yml exists
                existing_config = self._get_file_content("_config.yml")
                sha = existing_config.get('sha') if existing_config else None
                
                # Upload configuration
                result = self._create_or_update_file(
                    "_config.yml",
                    config_content,
                    "Setup Jekyll configuration for NOOBIE AI blog",
                    sha
                )
                
                if result:
                    return PublishResult(
                        success=True,
                        message="Jekyll configuration setup successfully"
                    )
                else:
                    return PublishResult(
                        success=False,
                        message="Failed to setup Jekyll configuration"
                    )
                    
            except Exception as e:
                return PublishResult(
                    success=False,
                    message=f"Error setting up Jekyll config: {str(e)}",
                    errors=[str(e)]
                )
    
    def create_index_page(self) -> PublishResult:
        """Create the main index page for the blog"""
        
        index_content = f"""---
layout: home
title: "{self.config.blog_title}"
description: "{self.config.blog_description}"
---

# Welcome to {self.config.blog_title}

{self.config.blog_description}

## Latest Posts

<div class="post-list">
{{% for post in site.posts limit:5 %}}
  <article class="post-preview">
    <h3><a href="{{{{ post.url }}}}">{{{{ post.title }}}}</a></h3>
    <p class="post-meta">{{{{ post.date | date: "%B %d, %Y" }}}} • {{{{ post.reading_time }}}} min read</p>
    <p>{{{{ post.excerpt | strip_html | truncate: 200 }}}}</p>
    <a href="{{{{ post.url }}}}" class="read-more">Read more →</a>
  </article>
{{% endfor %}}
</div>

## About NOOBIE AI

NOOBIE AI is an advanced artificial intelligence system that analyzes global news and generates thoughtful daily blog posts. Our AI examines multiple news sources, identifies key themes, and creates insightful commentary that goes beyond simple news reporting.

### What Makes NOOBIE AI Special?

- **🤖 AI-Powered Analysis**: Advanced language models process and analyze news from multiple sources
- **📰 Daily Updates**: Fresh content generated automatically every morning at 8:00 AM UTC
- **🌍 Global Perspective**: Comprehensive coverage of international developments
- **💡 Thoughtful Commentary**: Analysis that provides context and insights

### Latest Statistics

- **Total Posts**: {{{{ site.posts.size }}}}
- **Categories Covered**: Politics, Technology, Economics, International Affairs
- **Average Reading Time**: 5-8 minutes per post
- **Update Frequency**: Daily at 8:00 AM UTC

---

*Powered by artificial intelligence • Built with Jekyll • Hosted on GitHub Pages*
"""
        
        try:
            existing_index = self._get_file_content("index.md")
            sha = existing_index.get('sha') if existing_index else None
            
            result = self._create_or_update_file(
                "index.md",
                index_content,
                "Create/update blog index page",
                sha
            )
            
            if result:
                return PublishResult(
                    success=True,
                    message="Index page created successfully"
                )
            else:
                return PublishResult(
                    success=False,
                    message="Failed to create index page"
                )
                
        except Exception as e:
            return PublishResult(
                success=False,
                message=f"Error creating index page: {str(e)}",
                errors=[str(e)]
            )
    
    def get_repository_info(self) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        
        endpoint = f"/repos/{self.config.github_repo}"
        return self._make_api_request('GET', endpoint)
    
    def list_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent blog posts from the repository"""
        
        endpoint = f"/repos/{self.config.github_repo}/contents/_posts"
        
        response = self._make_api_request('GET', endpoint)
        
        if response and isinstance(response, list):
            # Sort by name (which includes date) and take most recent
            posts = sorted(response, key=lambda x: x['name'], reverse=True)
            return posts[:limit]
        
        return []