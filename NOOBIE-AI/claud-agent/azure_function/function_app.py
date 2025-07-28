"""
NOOBIE AI Azure Function App
============================

Main Azure Functions application with timer-triggered daily blog generation
and HTTP-triggered manual operations.
"""

import logging
import azure.functions as func
from datetime import datetime, timezone
import json
import traceback
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from claud_agent.config import load_config
from claud_agent.logger import setup_logging, get_logger, LogOperation
from claud_agent.news_fetcher import NewsFetcher
from claud_agent.blog_writer import BlogWriter
from claud_agent.github_publisher import GitHubPublisher

# Initialize the function app
app = func.FunctionApp()

# Configure logging for Azure
setup_logging(log_level="INFO", enable_console=True, enable_file=False)
logger = get_logger("noobie_ai.azure_function")

@app.timer_trigger(schedule="0 0 8 * * *", arg_name="timer", run_on_startup=False,
                  use_monitor=False) 
def daily_blog_generation(timer: func.TimerRequest) -> None:
    """
    Daily timer-triggered function that runs at 8:00 AM UTC.
    Fetches news, generates blog post, and publishes to GitHub Pages.
    """
    
    with LogOperation("Daily blog generation", logger):
        try:
            logger.info("🚀 Starting daily blog generation")
            
            # Load configuration
            config = load_config()
            logger.info("📋 Configuration loaded", extra_data=config.to_dict())
            
            # Validate configuration
            validation_errors = config.validate()
            if validation_errors:
                error_msg = f"Configuration validation failed: {validation_errors}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Initialize components
            news_fetcher = NewsFetcher(config)
            blog_writer = BlogWriter(config)
            github_publisher = GitHubPublisher(config)
            
            # Fetch trending news
            logger.info("📰 Fetching trending news articles")
            articles = news_fetcher.fetch_trending_news()
            
            if not articles:
                logger.warning("⚠️ No articles found - using mock mode")
                config.mock_mode = True
                articles = news_fetcher.generate_mock_articles("global-news", count=3)
            
            logger.info(f"✅ Fetched {len(articles)} articles for processing")
            
            # Generate blog post
            logger.info("✍️ Generating blog post from articles")
            blog_post = blog_writer.generate_blog_post(articles)
            
            if not blog_post:
                raise Exception("Failed to generate blog post")
            
            logger.info(f"✅ Blog post generated: '{blog_post.title}' ({blog_post.word_count} words)")
            
            # Setup Jekyll configuration if needed
            logger.info("🏗️ Setting up Jekyll configuration")
            jekyll_result = github_publisher.setup_jekyll_config()
            if not jekyll_result.success:
                logger.warning(f"Jekyll setup warning: {jekyll_result.message}")
            
            # Create index page
            index_result = github_publisher.create_index_page()
            if not index_result.success:
                logger.warning(f"Index page warning: {index_result.message}")
            
            # Publish to GitHub Pages
            logger.info("📤 Publishing blog post to GitHub Pages")
            publish_result = github_publisher.publish_blog_post(blog_post)
            
            if publish_result.success:
                logger.info(f"🎉 Blog post published successfully!", extra_data={
                    'title': blog_post.title,
                    'url': publish_result.url,
                    'commit_sha': publish_result.commit_sha,
                    'word_count': blog_post.word_count,
                    'tags': blog_post.tags
                })
            else:
                raise Exception(f"Publishing failed: {publish_result.message}")
            
            # Log execution statistics
            execution_stats = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'articles_fetched': len(articles),
                'blog_title': blog_post.title,
                'word_count': blog_post.word_count,
                'tags_count': len(blog_post.tags),
                'publish_url': publish_result.url,
                'success': True
            }
            
            logger.info("📊 Daily blog generation completed successfully", extra_data=execution_stats)
            
        except Exception as e:
            error_msg = f"Daily blog generation failed: {str(e)}"
            logger.error(error_msg, extra_data={
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            })
            raise


@app.route(route="manual_generate", auth_level=func.AuthLevel.FUNCTION)
def manual_blog_generation(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered function for manual blog generation.
    Accepts POST requests with optional parameters.
    """
    
    logger.info("🔧 Manual blog generation triggered")
    
    try:
        # Parse request parameters
        try:
            req_body = req.get_json() or {}
        except ValueError:
            req_body = {}
        
        # Override configuration if provided
        config = load_config()
        if 'mock_mode' in req_body:
            config.mock_mode = bool(req_body['mock_mode'])
        if 'max_articles' in req_body:
            config.max_articles = int(req_body.get('max_articles', config.max_articles))
        
        logger.info("⚙️ Manual generation parameters", extra_data=req_body)
        
        # Run the same logic as daily generation
        news_fetcher = NewsFetcher(config)
        blog_writer = BlogWriter(config)
        github_publisher = GitHubPublisher(config)
        
        # Fetch articles
        articles = news_fetcher.fetch_trending_news()
        if not articles and config.mock_mode:
            articles = news_fetcher.generate_mock_articles("breaking-news", count=3)
        
        if not articles:
            return func.HttpResponse(
                json.dumps({"error": "No articles found"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Generate blog post
        blog_post = blog_writer.generate_blog_post(articles)
        if not blog_post:
            return func.HttpResponse(
                json.dumps({"error": "Failed to generate blog post"}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Publish
        publish_result = github_publisher.publish_blog_post(blog_post)
        
        response_data = {
            "success": publish_result.success,
            "message": publish_result.message,
            "blog_title": blog_post.title,
            "word_count": blog_post.word_count,
            "url": publish_result.url,
            "commit_sha": publish_result.commit_sha,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if publish_result.success:
            logger.info("✅ Manual generation completed successfully", extra_data=response_data)
            return func.HttpResponse(
                json.dumps(response_data),
                status_code=200,
                mimetype="application/json"
            )
        else:
            logger.error("❌ Manual generation failed", extra_data=response_data)
            return func.HttpResponse(
                json.dumps(response_data),
                status_code=500,
                mimetype="application/json"
            )
            
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.error("❌ Manual generation error", extra_data=error_response)
        
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint for monitoring.
    """
    
    try:
        config = load_config()
        validation_errors = config.validate()
        
        health_data = {
            "status": "healthy" if not validation_errors else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "configuration": {
                "has_news_api": bool(config.news_api_key),
                "has_claude_api": bool(config.claude_api_key),
                "has_github_token": bool(config.github_token),
                "github_repo": config.github_repo,
                "max_articles": config.max_articles
            },
            "validation_errors": validation_errors
        }
        
        status_code = 200 if not validation_errors else 503
        
        return func.HttpResponse(
            json.dumps(health_data, indent=2),
            status_code=status_code,
            mimetype="application/json"
        )
        
    except Exception as e:
        error_data = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(error_data),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="status", auth_level=func.AuthLevel.FUNCTION)
def get_system_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    Detailed system status endpoint with recent posts information.
    """
    
    try:
        config = load_config()
        github_publisher = GitHubPublisher(config)
        
        # Get repository information
        repo_info = github_publisher.get_repository_info()
        recent_posts = github_publisher.list_recent_posts(limit=5)
        
        status_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_status": "operational",
            "configuration": config.to_dict(),
            "repository": {
                "name": repo_info.get('name') if repo_info else None,
                "full_name": repo_info.get('full_name') if repo_info else None,
                "description": repo_info.get('description') if repo_info else None,
                "homepage": repo_info.get('homepage') if repo_info else None,
                "has_pages": repo_info.get('has_pages') if repo_info else False
            },
            "recent_posts": [
                {
                    "name": post['name'],
                    "size": post['size'],
                    "download_url": post.get('download_url')
                } for post in recent_posts
            ],
            "next_scheduled_run": "Daily at 8:00 AM UTC"
        }
        
        return func.HttpResponse(
            json.dumps(status_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        error_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_status": "error",
            "error": str(e)
        }
        
        return func.HttpResponse(
            json.dumps(error_data),
            status_code=500,
            mimetype="application/json"
        )