#!/bin/bash

# ================================================================================
# NOOBIE AI - AZURE FUNCTIONS DEPLOYMENT SCRIPT
# ================================================================================
# Professional-grade deployment script for NOOBIE AI blog generation system
# Author: Akhil Reddy
# GitHub: akhilreddydanda/NOOBIE
# ================================================================================

set -e  # Exit immediately if a command exits with a non-zero status

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="noobie-ai-rg"
LOCATION="East US"
STORAGE_ACCOUNT="noobieaistorage$(date +%s)"
FUNCTION_APP="noobieAI$(date +%s)"
PYTHON_VERSION="3.11"
GITHUB_REPO="akhilreddydanda/NOOBIE"

# Logging function
log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner
echo -e "${PURPLE}"
cat << "EOF"
 _   _  ___   ___  ____  _____ _____      _    _____ 
| \ | |/ _ \ / _ \| __ )|_ _| | ____|    / \  |_ _|
|  \| | | | | | | |  _ \ | |  |  _|     / _ \  | | 
| |\  | |_| | |_| | |_) || |  | |___   / ___ \ | | 
|_| \_|\___/ \___/|____/|___| |_____| /_/   \_\___|
                                                   
    Azure Functions Deployment System
    Enterprise-Grade AI Blog Automation
EOF
echo -e "${NC}"

log "🚀 Starting NOOBIE AI deployment to Azure Functions..."
log "📋 Configuration:"
log "   • Resource Group: ${RESOURCE_GROUP}"
log "   • Location: ${LOCATION}"
log "   • Storage Account: ${STORAGE_ACCOUNT}"
log "   • Function App: ${FUNCTION_APP}"
log "   • Python Version: ${PYTHON_VERSION}"
log "   • GitHub Repository: ${GITHUB_REPO}"
echo ""

# Prerequisites check
log "🔍 Checking prerequisites..."

# Check Azure CLI
if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed. Installing now..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    success "Azure CLI installed successfully"
else
    success "Azure CLI found: $(az version --query '"azure-cli"' -o tsv)"
fi

# Check Azure Functions Core Tools
if ! command -v func &> /dev/null; then
    error "Azure Functions Core Tools not found. Installing now..."
    npm install -g azure-functions-core-tools@4 --unsafe-perm true
    success "Azure Functions Core Tools installed successfully"
else
    success "Azure Functions Core Tools found: $(func --version)"
fi

# Check Azure login
log "🔐 Checking Azure authentication..."
if ! az account show &> /dev/null; then
    error "Not logged in to Azure. Please run: az login"
    exit 1
else
    ACCOUNT_NAME=$(az account show --query user.name -o tsv)
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    success "Logged in as: ${ACCOUNT_NAME}"
    log "   • Subscription: ${SUBSCRIPTION_ID}"
fi

# Check for configuration file
if [[ ! -f "azure_settings.json" ]]; then
    warning "azure_settings.json not found. Creating template..."
    cat > azure_settings.json << 'EOL'
[
  {
    "name": "NEWS_API_KEY",
    "value": "your-gnews-api-key-here",
    "slotSetting": false
  },
  {
    "name": "CLAUDE_API_KEY",
    "value": "your-claude-api-key-here",
    "slotSetting": false
  },
  {
    "name": "GITHUB_TOKEN",
    "value": "your-github-token-here",
    "slotSetting": false
  },
  {
    "name": "GITHUB_REPO",
    "value": "akhilreddydanda/NOOBIE",
    "slotSetting": false
  },
  {
    "name": "UPLOAD_TO_GITHUB",
    "value": "true",
    "slotSetting": false
  },
  {
    "name": "MAX_ARTICLES",
    "value": "8",
    "slotSetting": false
  },
  {
    "name": "LOG_LEVEL",
    "value": "INFO",
    "slotSetting": false
  }
]
EOL
    warning "Please edit azure_settings.json with your actual API keys before continuing!"
    read -p "Have you updated azure_settings.json with your API keys? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Please update azure_settings.json with your API keys and run this script again."
        exit 1
    fi
fi

echo ""
log "🏗️  Creating Azure resources..."

# Create resource group
log "📁 Creating resource group: ${RESOURCE_GROUP}"
az group create \
    --name "${RESOURCE_GROUP}" \
    --location "${LOCATION}" \
    --output table

success "Resource group created successfully"

# Create storage account
log "💾 Creating storage account: ${STORAGE_ACCOUNT}"
az storage account create \
    --name "${STORAGE_ACCOUNT}" \
    --location "${LOCATION}" \
    --resource-group "${RESOURCE_GROUP}" \
    --sku Standard_LRS \
    --output table

success "Storage account created successfully"

# Create function app
log "⚡ Creating function app: ${FUNCTION_APP}"
az functionapp create \
    --resource-group "${RESOURCE_GROUP}" \
    --consumption-plan-location "${LOCATION}" \
    --runtime python \
    --runtime-version "${PYTHON_VERSION}" \
    --functions-version 4 \
    --name "${FUNCTION_APP}" \
    --storage-account "${STORAGE_ACCOUNT}" \
    --os-type Linux \
    --output table

success "Function app created successfully"

# Configure application settings
log "⚙️  Configuring application settings..."
az functionapp config appsettings set \
    --name "${FUNCTION_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --settings @azure_settings.json \
    --output table

success "Application settings configured"

# Create local.settings.json for local development
log "📁 Creating local development settings..."
cat > local.settings.json << EOL
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "NEWS_API_KEY": "your-gnews-api-key-here",
    "CLAUDE_API_KEY": "your-claude-api-key-here",
    "GITHUB_TOKEN": "your-github-token-here",
    "GITHUB_REPO": "${GITHUB_REPO}",
    "UPLOAD_TO_GITHUB": "true",
    "MAX_ARTICLES": "8",
    "LOG_LEVEL": "INFO"
  }
}
EOL

# Deploy the function
log "🚀 Deploying NOOBIE AI to Azure Functions..."
log "   • Packaging application..."
log "   • Uploading to Azure..."

if func azure functionapp publish "${FUNCTION_APP}" --python; then
    success "Function deployed successfully!"
else
    error "Function deployment failed!"
    exit 1
fi

# Enable Application Insights
log "📊 Setting up Application Insights for monitoring..."
INSTRUMENTATION_KEY=$(az monitor app-insights component create \
    --app "${FUNCTION_APP}" \
    --location "${LOCATION}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query 'instrumentationKey' \
    --output tsv)

az functionapp config appsettings set \
    --name "${FUNCTION_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --settings "APPINSIGHTS_INSTRUMENTATIONKEY=${INSTRUMENTATION_KEY}" \
    --output table

success "Application Insights configured"

# Verify deployment
log "🔍 Verifying deployment..."
FUNCTION_STATE=$(az functionapp show \
    --name "${FUNCTION_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query "state" \
    --output tsv)

if [[ "${FUNCTION_STATE}" == "Running" ]]; then
    success "Function app is running successfully!"
else
    warning "Function app state: ${FUNCTION_STATE}"
fi

# Display deployment summary
echo ""
echo -e "${GREEN}🎉 NOOBIE AI DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo "==============================================="
echo ""
echo -e "${CYAN}📋 Deployment Summary:${NC}"
echo "   • Function App Name: ${FUNCTION_APP}"
echo "   • Function URL: https://${FUNCTION_APP}.azurewebsites.net"
echo "   • Resource Group: ${RESOURCE_GROUP}"
echo "   • Region: ${LOCATION}"
echo "   • Runtime: Python ${PYTHON_VERSION}"
echo "   • Schedule: Daily at 8:00 AM UTC"
echo ""
echo -e "${CYAN}🔗 Important URLs:${NC}"
echo "   • Azure Portal: https://portal.azure.com"
echo "   • Function Management: https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Web/sites/${FUNCTION_APP}"
echo "   • GitHub Repository: https://github.com/${GITHUB_REPO}"
echo ""
echo -e "${CYAN}📊 Monitoring Commands:${NC}"
echo "   • View logs: az functionapp logs tail --name ${FUNCTION_APP} --resource-group ${RESOURCE_GROUP}"
echo "   • Function status: az functionapp show --name ${FUNCTION_APP} --resource-group ${RESOURCE_GROUP}"
echo "   • Restart function: az functionapp restart --name ${FUNCTION_APP} --resource-group ${RESOURCE_GROUP}"
echo ""
echo -e "${CYAN}🔧 Management Commands:${NC}"
echo "   • Update settings: az functionapp config appsettings set --name ${FUNCTION_APP} --resource-group ${RESOURCE_GROUP} --settings 'KEY=value'"
echo "   • Delete resources: az group delete --name ${RESOURCE_GROUP} --yes --no-wait"
echo ""
echo -e "${YELLOW}💡 What happens next:${NC}"
echo "   1. 🕒 NOOBIE AI will run automatically at 8:00 AM UTC daily"
echo "   2. 📰 Fetch trending news from multiple sources"
echo "   3. 🤖 Generate AI blog posts using Claude"
echo "   4. 📤 Upload to GitHub repository: ${GITHUB_REPO}"
echo "   5. 📊 Log detailed execution statistics"
echo ""
echo -e "${GREEN}🚀 Your NOOBIE AI system is now live and running 24/7!${NC}"
echo ""

# Save deployment info
cat > deployment_info.json << EOL
{
  "deployment_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "function_app_name": "${FUNCTION_APP}",
  "resource_group": "${RESOURCE_GROUP}",
  "location": "${LOCATION}",
  "function_url": "https://${FUNCTION_APP}.azurewebsites.net",
  "github_repo": "${GITHUB_REPO}",
  "schedule": "Daily at 8:00 AM UTC",
  "status": "deployed"
}
EOL

success "Deployment information saved to deployment_info.json"
log "🎯 NOOBIE AI deployment completed successfully!"