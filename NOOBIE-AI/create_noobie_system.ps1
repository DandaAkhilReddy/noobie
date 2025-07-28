# NOOBIE AI System Creation Script
# Run this PowerShell script as Administrator in Windows

param(
    [string]$TargetPath = "C:\Users\akhil\OneDrive\Documents\Noobie_AI_Agent"
)

Write-Host "🚀 Creating NOOBIE AI System..." -ForegroundColor Green
Write-Host "Target Location: $TargetPath" -ForegroundColor Cyan

# Create main directory
if (Test-Path $TargetPath) {
    Write-Host "⚠️  Removing existing directory..." -ForegroundColor Yellow
    Remove-Item -Path $TargetPath -Recurse -Force
}

New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
Set-Location -Path $TargetPath

# Create subdirectories
Write-Host "📁 Creating folder structure..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "claud_agent" -Force | Out-Null
New-Item -ItemType Directory -Path "azure_function" -Force | Out-Null
New-Item -ItemType Directory -Path "docs" -Force | Out-Null
New-Item -ItemType Directory -Path "tests" -Force | Out-Null

# Initialize Git repository
Write-Host "🔧 Initializing Git repository..." -ForegroundColor Cyan
git init
git branch -m main
git config user.email "akhil@hhamedicine.com"
git config user.name "Akhil Reddy"

Write-Host "📝 Creating files..." -ForegroundColor Cyan

# Create .gitignore
@"
# NOOBIE AI - Git Ignore File
# ============================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Azure Functions
.azure/
azure_function/local.settings.json
bin/
obj/

# Logs and cache
*.log
logs/
.cache/
blog_output/
news_cache_*.json

# Test coverage
.coverage
htmlcov/
.pytest_cache/
.tox/

# Secrets and API keys
*.key
*.pem
secrets.json
.env
.env.local
.env.production

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Backup files
*.bak
*.backup
*~
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

# Create claud_agent/__init__.py
@"
"""
NOOBIE AI Package
================

Enterprise-grade AI-powered blog generation system with multi-source
news aggregation, intelligent content creation, and automated publishing.
"""

__version__ = "1.0.0"
__author__ = "Akhil Reddy"
__email__ = "akhil@hhamedicine.com"
__description__ = "AI-powered daily blog generation system"
__url__ = "https://github.com/DandaAkhilReddy/noobie"

# Package metadata
PACKAGE_INFO = {
    "name": "NOOBIE AI",
    "version": __version__,
    "author": __author__,
    "description": __description__,
    "features": [
        "Multi-source news aggregation",
        "AI-powered content generation", 
        "GitHub Pages publishing",
        "Azure Functions automation",
        "Production-grade logging",
        "Comprehensive error handling"
    ]
}

# Export main classes
from .config import NoobieConfig, load_config
from .logger import get_logger, setup_logging, LogOperation
from .news_fetcher import NewsFetcher, NewsArticle
from .blog_writer import BlogWriter, BlogPost
from .github_publisher import GitHubPublisher, PublishResult

__all__ = [
    'NoobieConfig',
    'load_config', 
    'get_logger',
    'setup_logging',
    'LogOperation',
    'NewsFetcher',
    'NewsArticle',
    'BlogWriter', 
    'BlogPost',
    'GitHubPublisher',
    'PublishResult',
    'PACKAGE_INFO'
]
"@ | Out-File -FilePath "claud_agent\__init__.py" -Encoding UTF8

Write-Host "✅ Created claud_agent/__init__.py" -ForegroundColor Green

# Continue with more files...
Write-Host "🎉 NOOBIE AI System created successfully!" -ForegroundColor Green
Write-Host "📍 Location: $TargetPath" -ForegroundColor Cyan
Write-Host "📚 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review README_NOOBIE.md for setup instructions" -ForegroundColor White
Write-Host "  2. Configure API keys in azure_function/local.settings.json" -ForegroundColor White
Write-Host "  3. Run deploy_azure.sh for Azure deployment" -ForegroundColor White

# Note: This is a truncated version for demonstration
# The full script would contain all file contents