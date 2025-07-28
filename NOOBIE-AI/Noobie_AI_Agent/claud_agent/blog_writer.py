"""
NOOBIE AI Blog Writer
====================

Advanced AI-powered blog generation using Claude and OpenAI APIs
with intelligent content structuring and SEO optimization.
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

from .logger import get_logger, LogOperation
from .config import NoobieConfig
from .news_fetcher import NewsArticle

@dataclass
class BlogPost:
    """Data class for generated blog posts"""
    title: str
    content: str
    summary: str
    tags: List[str]
    category: str
    publication_date: str
    author: str
    word_count: int
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    featured_image: Optional[str] = None
    
    def to_markdown(self) -> str:
        """Convert blog post to markdown with frontmatter"""
        
        # Create frontmatter
        frontmatter = f"""---
layout: post
title: "{self.title}"
date: {self.publication_date}
author: "{self.author}"
categories: [{self.category}]
tags: [{', '.join(f'"{tag}"' for tag in self.tags)}]
excerpt: "{self.summary}"
seo_title: "{self.seo_title or self.title}"
seo_description: "{self.seo_description or self.summary}"
word_count: {self.word_count}
---

"""
        
        return frontmatter + self.content
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blog post to dictionary"""
        return {
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'tags': self.tags,
            'category': self.category,
            'publication_date': self.publication_date,
            'author': self.author,
            'word_count': self.word_count,
            'seo_title': self.seo_title,
            'seo_description': self.seo_description,
            'featured_image': self.featured_image
        }

class BlogWriter:
    """
    Advanced AI blog writer with multiple model support and intelligent content generation
    """
    
    def __init__(self, config: NoobieConfig):
        self.config = config
        self.logger = get_logger(__name__)
        
        # AI API endpoints
        self.claude_api_url = "https://api.anthropic.com/v1/messages"
        self.openai_api_url = "https://api.openai.com/v1/chat/completions"
        
        # Content templates
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load the system prompt for AI content generation"""
        
        default_prompt = f"""You are NOOBIE AI, an intelligent blog writer that creates thoughtful, engaging daily blog posts about global news and trends.

Your writing style:
- Professional yet accessible tone
- Analytical and insightful commentary
- Well-structured with clear headings
- SEO-optimized content
- Engaging introduction and conclusion
- Use of relevant examples and context

Blog specifications:
- Target audience: Educated readers interested in global affairs
- Word count: 800-1500 words
- Include 3-5 main sections with subheadings
- Add relevant tags and categories
- Create compelling headlines
- Focus on analysis rather than just reporting

Author: {self.config.author_name}
Blog: {self.config.blog_title}

Always maintain objectivity while providing thoughtful analysis of current events."""

        return default_prompt
    
    def _create_content_prompt(self, articles: List[NewsArticle]) -> str:
        """Create the content generation prompt from articles"""
        
        articles_text = "\n\n".join([
            f"**Article {i+1}:**\n"
            f"Title: {article.title}\n"
            f"Source: {article.source}\n"
            f"Summary: {article.summary}\n"
            f"Category: {article.category}\n"
            f"URL: {article.url}"
            for i, article in enumerate(articles)
        ])
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"""Based on the following news articles from {current_date}, create a comprehensive blog post that analyzes the key themes and developments:

{articles_text}

Please create a blog post with:
1. A compelling title that captures the main themes
2. An engaging introduction
3. 3-4 main sections with descriptive subheadings
4. Thoughtful analysis connecting the different stories
5. A conclusion that looks forward to implications
6. Appropriate tags and categories

The blog post should be informative, well-researched, and provide unique insights beyond just summarizing the news. Focus on connecting themes across different stories and providing valuable analysis for readers interested in understanding global developments.

Format the response as a complete blog post in markdown format."""

        return prompt
    
    def _call_claude_api(self, prompt: str) -> Optional[str]:
        """Call Claude API for content generation"""
        
        if not self.config.claude_api_key:
            self.logger.warning("🔑 Claude API key not configured")
            return None
        
        with LogOperation("Claude API call", self.logger):
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.config.claude_api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "temperature": 0.7,
                "system": self.system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            try:
                response = requests.post(
                    self.claude_api_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                
                response.raise_for_status()
                data = response.json()
                
                if 'content' in data and data['content']:
                    content = data['content'][0].get('text', '')
                    self.logger.info(f"✅ Claude API response received ({len(content)} characters)")
                    return content
                else:
                    self.logger.error("❌ Invalid response format from Claude API")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ Claude API request failed: {e}")
                return None
            except Exception as e:
                self.logger.error(f"❌ Error processing Claude API response: {e}")
                return None
    
    def _call_openai_api(self, prompt: str) -> Optional[str]:
        """Call OpenAI API as fallback"""
        
        if not self.config.openai_api_key:
            self.logger.warning("🔑 OpenAI API key not configured")
            return None
        
        with LogOperation("OpenAI API call", self.logger):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.openai_api_key}"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            try:
                response = requests.post(
                    self.openai_api_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                
                response.raise_for_status()
                data = response.json()
                
                if 'choices' in data and data['choices']:
                    content = data['choices'][0]['message']['content']
                    self.logger.info(f"✅ OpenAI API response received ({len(content)} characters)")
                    return content
                else:
                    self.logger.error("❌ Invalid response format from OpenAI API")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ OpenAI API request failed: {e}")
                return None
            except Exception as e:
                self.logger.error(f"❌ Error processing OpenAI API response: {e}")
                return None
    
    def _generate_mock_content(self, articles: List[NewsArticle]) -> str:
        """Generate mock content for testing"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        categories = list(set(article.category for article in articles))
        
        mock_content = f"""# Today's Global Pulse - {current_date}

*Generated by NOOBIE AI - Your Daily News Intelligence System*

## Executive Summary

In examining today's global developments, several key themes emerge that deserve thoughtful analysis. Our AI system has analyzed {len(articles)} articles across {len(categories)} categories to bring you this comprehensive overview.

## Political Developments

Recent political developments continue to shape the international landscape. The interconnected nature of global politics means that decisions in one region often have far-reaching implications across multiple continents.

### Key Political Trends

- International diplomatic initiatives show continued engagement
- Policy decisions reflect growing focus on economic security
- Regional cooperation efforts demonstrate multilateral approaches

## Economic Indicators

Global markets continue to demonstrate resilience in the face of various challenges. Current economic indicators suggest a complex but generally positive outlook for sustained growth.

### Market Analysis

The current economic environment rewards adaptability and innovation. Organizations that can balance efficiency with resilience appear best positioned for long-term success.

## Technology and Innovation

The pace of technological advancement continues to accelerate, with artificial intelligence and automation reshaping industries globally. Today's developments highlight both tremendous opportunities and important responsibilities.

### AI Integration Trends

As AI systems like NOOBIE AI become more capable of generating thoughtful analysis, we're reminded that technology's greatest value lies in augmenting human judgment rather than replacing it.

## International Affairs

Regional developments across different continents continue to influence global dynamics. From diplomatic initiatives to economic partnerships, today's international landscape reflects both challenges and opportunities.

### Global Cooperation

The most successful international initiatives appear to be those that recognize both national sovereignty and the benefits of collaborative problem-solving.

## Looking Forward

As we analyze today's developments through our AI lens, several patterns emerge that may offer insights into future trends:

1. **Technological Integration**: Seamless AI incorporation continues to accelerate
2. **Economic Adaptation**: Markets show remarkable flexibility and innovation
3. **Global Cooperation**: Evidence of continued international collaboration
4. **Information Analysis**: AI's growing role in processing and presenting complex information

## Conclusion

Today's analysis reinforces the importance of staying informed about global developments while maintaining perspective on long-term trends. NOOBIE AI will continue providing daily insights to help navigate our complex world.

---

**About NOOBIE AI**: This post was generated by an advanced artificial intelligence system designed to analyze global news and provide thoughtful daily commentary.

*Next update: Tomorrow at 8:00 AM UTC*"""

        self.logger.info("🎭 Generated mock blog content for testing")
        return mock_content
    
    def generate_blog_post(self, articles: List[NewsArticle]) -> Optional[BlogPost]:
        """Generate a complete blog post from news articles"""
        
        if not articles:
            self.logger.error("❌ No articles provided for blog generation")
            return None
        
        with LogOperation(f"Blog generation from {len(articles)} articles", self.logger):
            
            # Create content prompt
            content_prompt = self._create_content_prompt(articles)
            
            # Try to generate content with AI APIs
            blog_content = None
            
            # Try Claude first
            if self.config.claude_api_key:
                blog_content = self._call_claude_api(content_prompt)
            
            # Fallback to OpenAI
            if not blog_content and self.config.openai_api_key:
                self.logger.info("🔄 Falling back to OpenAI API")
                blog_content = self._call_openai_api(content_prompt)
            
            # Fallback to mock content
            if not blog_content:
                self.logger.warning("🎭 Using mock content generation")
                blog_content = self._generate_mock_content(articles)
            
            if not blog_content:
                self.logger.error("❌ Failed to generate blog content")
                return None
            
            # Parse and structure the blog post
            blog_post = self._parse_blog_content(blog_content, articles)
            
            self.logger.info(f"✅ Blog post generated successfully", extra_data={
                'title': blog_post.title,
                'word_count': blog_post.word_count,
                'tags': blog_post.tags,
                'category': blog_post.category
            })
            
            return blog_post
    
    def _parse_blog_content(self, content: str, source_articles: List[NewsArticle]) -> BlogPost:
        """Parse AI-generated content into structured blog post"""
        
        # Extract title (usually the first # heading)
        title_match = re.search(r'#\s+(.+)', content)
        title = title_match.group(1).strip() if title_match else f"Daily Global Analysis - {datetime.now().strftime('%B %d, %Y')}"
        
        # Generate summary from first paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        summary = paragraphs[0][:200] + "..." if paragraphs else "Daily AI-powered analysis of global news and trends."
        
        # Extract categories from source articles
        categories = list(set(article.category for article in source_articles))
        primary_category = categories[0] if categories else "global-news"
        
        # Generate tags
        tags = self._generate_tags(content, source_articles)
        
        # Calculate word count
        word_count = len(content.split())
        
        # Generate SEO elements
        seo_title = f"{title} | {self.config.blog_title}"
        seo_description = summary[:155] + "..." if len(summary) > 155 else summary
        
        blog_post = BlogPost(
            title=title,
            content=content,
            summary=summary,
            tags=tags,
            category=primary_category,
            publication_date=datetime.now().isoformat(),
            author=self.config.author_name,
            word_count=word_count,
            seo_title=seo_title,
            seo_description=seo_description
        )
        
        return blog_post
    
    def _generate_tags(self, content: str, articles: List[NewsArticle]) -> List[str]:
        """Generate relevant tags from content and source articles"""
        
        # Base tags
        tags = ["daily-update", "ai-generated", "global-news", "analysis"]
        
        # Add category-based tags
        for article in articles:
            category_words = article.category.lower().split()
            tags.extend(category_words)
        
        # Add content-based tags
        content_lower = content.lower()
        
        # Common topic keywords
        topic_keywords = {
            'politics': ['political', 'government', 'policy', 'election'],
            'economics': ['economic', 'market', 'financial', 'trade'],
            'technology': ['technology', 'ai', 'digital', 'innovation'],
            'international': ['international', 'global', 'world', 'diplomatic'],
            'business': ['business', 'corporate', 'industry', 'company']
        }
        
        for tag, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)
        
        # Remove duplicates and limit
        unique_tags = list(set(tags))[:10]
        
        return unique_tags
    
    def save_blog_post(self, blog_post: BlogPost, output_dir: str = "blog_output") -> str:
        """Save blog post to file"""
        
        from pathlib import Path
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        title_slug = re.sub(r'[^\w\s-]', '', blog_post.title.lower())
        title_slug = re.sub(r'[\s_-]+', '-', title_slug)[:50]
        filename = f"{date_str}-{title_slug}.md"
        
        file_path = output_path / filename
        
        # Save as markdown
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(blog_post.to_markdown())
        
        self.logger.info(f"💾 Blog post saved to: {file_path}")
        
        # Also save as JSON for backup
        json_path = output_path / f"{date_str}-{title_slug}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(blog_post.to_dict(), f, indent=2, ensure_ascii=False)
        
        return str(file_path)