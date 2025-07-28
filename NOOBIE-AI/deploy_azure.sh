#!/bin/bash

# NOOBIE AI - Azure Functions Deployment Script
# This script deploys the NOOBIE AI system to Azure Functions for daily automated execution

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="noobie-ai-rg"
LOCATION="East US"
STORAGE_ACCOUNT="noobieaistorage$(date +%s)"  # Add timestamp to avoid conflicts
FUNCTION_APP="noobieAI$(date +%s)"
PYTHON_VERSION="3.11"

echo "🤖 NOOBIE AI - AZURE DEPLOYMENT STARTING"
echo "========================================"
echo "🚀 Deploying your AI blog generation system to Azure..."
echo ""
echo "📋 Configuration:"
echo "   • Resource Group: $RESOURCE_GROUP"
echo "   • Location: $LOCATION"
echo "   • Storage Account: $STORAGE_ACCOUNT"
echo "   • Function App: $FUNCTION_APP"
echo "   • Python Version: $PYTHON_VERSION"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Installing now..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Check if Azure Functions Core Tools is installed
if ! command -v func &> /dev/null; then
    echo "❌ Azure Functions Core Tools not installed. Installing now..."
    npm install -g azure-functions-core-tools@4 --unsafe-perm true
fi

# Check if user is logged in to Azure
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Please login to Azure first:"
    echo "   az login"
    exit 1
fi

echo "✅ Prerequisites ready!"
echo ""

# Create resource group
echo "🏗️  Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output table

# Create storage account
echo "💾 Creating storage account: $STORAGE_ACCOUNT"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --location "$LOCATION" \
    --resource-group $RESOURCE_GROUP \
    --sku Standard_LRS \
    --output table

# Create function app
echo "⚡ Creating function app: $FUNCTION_APP"
az functionapp create \
    --resource-group $RESOURCE_GROUP \
    --consumption-plan-location "$LOCATION" \
    --runtime python \
    --runtime-version $PYTHON_VERSION \
    --functions-version 4 \
    --name $FUNCTION_APP \
    --storage-account $STORAGE_ACCOUNT \
    --os-type Linux \
    --output table

# Configure application settings
echo "⚙️  Configuring application settings..."
echo ""
echo "📝 IMPORTANT: Make sure you've updated azure_settings.json with your actual API keys!"
echo ""

az functionapp config appsettings set \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --settings @azure_settings.json \
    --output table

# Deploy the function
echo "🚀 Deploying NOOBIE AI to Azure Functions..."
func azure functionapp publish $FUNCTION_APP --python

# Enable Application Insights
echo "📊 Setting up monitoring..."
az functionapp config appsettings set \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$(az monitor app-insights component create --app $FUNCTION_APP --location '$LOCATION' --resource-group $RESOURCE_GROUP --query 'instrumentationKey' --output tsv)" \
    --output table

echo ""
echo "🎉 NOOBIE AI DEPLOYMENT COMPLETE!"
echo "================================="
echo "✅ Function App: $FUNCTION_APP.azurewebsites.net"
echo "✅ Resource Group: $RESOURCE_GROUP"
echo "✅ Schedule: Daily at 8:00 AM UTC"
echo "✅ Next execution: Tomorrow at 8:00 AM UTC"
echo ""
echo "📊 Monitor your NOOBIE AI:"
echo "   • Azure Portal: https://portal.azure.com"
echo "   • View logs: az functionapp logs tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP"
echo ""
echo "🤖 Your NOOBIE AI is now running automatically!"
echo "   Fresh blog posts will be generated daily at 8:00 AM UTC"