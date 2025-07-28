# 🤖 NOOBIE AI - Automated Blog Generation System

**Your Personal AI Blog Writer - Generates Fresh Content Daily**

## 🎯 What is NOOBIE AI?

NOOBIE AI is an intelligent system that automatically:
- 📰 **Fetches** trending news from multiple sources
- 🤖 **Analyzes** content using Claude AI
- ✍️ **Generates** thoughtful blog posts daily
- 📤 **Publishes** to GitHub Pages automatically
- 📊 **Logs** everything for monitoring

**Result**: Fresh, professional blog content every morning at 8:00 AM UTC!

---

## 🚀 Quick Deployment to Azure

### **Step 1: Prerequisites**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Login to Azure
az login
```

### **Step 2: Get API Keys**
1. **GNews API**: Visit [gnews.io](https://gnews.io) → Sign up → Get API key
2. **Claude API**: Visit [console.anthropic.com](https://console.anthropic.com) → Get API key
3. **GitHub Token**: Visit [github.com/settings/tokens](https://github.com/settings/tokens) → Generate token with `repo` permissions

### **Step 3: Configure Settings**
Edit `azure_settings.json` with your actual API keys:
```json
{
  "name": "NEWS_API_KEY",
  "value": "YOUR_ACTUAL_GNEWS_API_KEY"
},
{
  "name": "CLAUDE_API_KEY", 
  "value": "YOUR_ACTUAL_CLAUDE_API_KEY"
},
{
  "name": "GITHUB_TOKEN",
  "value": "YOUR_ACTUAL_GITHUB_TOKEN"
},
{
  "name": "GITHUB_REPO",
  "value": "yourusername/your-blog-repo"
}
```

### **Step 4: Deploy to Azure**
```bash
chmod +x deploy_azure.sh
./deploy_azure.sh
```

That's it! NOOBIE AI will now run daily at 8:00 AM UTC.

---

## 📁 File Structure

```
NOOBIE-AI/
├── azure_function/          # Azure Function code
│   ├── __init__.py          # Main function entry point
│   └── function.json        # Timer trigger configuration
├── noobie_core.py           # Core AI system logic
├── deploy_azure.sh          # Deployment script
├── azure_settings.json      # Environment variables
├── requirements.txt         # Dependencies
├── host.json               # Azure host configuration
└── README.md               # This file
```

---

## 🎯 How It Works

1. **⏰ Timer Trigger**: Azure Function runs daily at 8:00 AM UTC
2. **📰 News Fetching**: Collects trending articles from news APIs
3. **🤖 AI Generation**: Claude AI creates thoughtful blog posts
4. **📤 Auto-Publishing**: Uploads to GitHub Pages via GitHub API
5. **📊 Monitoring**: Logs execution details in Azure Portal

---

## 💰 Cost

- **Azure Functions**: ~$1.50/month
- **Storage**: ~$0.50/month
- **Monitoring**: ~$1.00/month
- **Total**: **~$3/month** for fully automated AI blogging!

---

## 📊 Monitoring

### View Live Logs
```bash
# Stream function logs
az functionapp logs tail --name [YOUR_FUNCTION_APP] --resource-group noobie-ai-rg

# Check function status
az functionapp show --name [YOUR_FUNCTION_APP] --resource-group noobie-ai-rg
```

### Azure Portal
- Go to [portal.azure.com](https://portal.azure.com)
- Navigate to your Function App
- Check execution history and logs

---

## 🛠️ Customization

### Change Schedule
Edit `azure_function/function.json`:
- `"0 0 12 * * *"` - Run at 12:00 PM UTC
- `"0 0 6,18 * * *"` - Run at 6:00 AM and 6:00 PM UTC

### Modify Content
Edit `noobie_core.py` to:
- Change news sources
- Adjust AI prompts
- Customize blog format

---

## 🎉 Success!

Once deployed, NOOBIE AI will:
- ✅ Generate fresh blog posts daily
- ✅ Never miss a day of content
- ✅ Cost less than a coffee per month
- ✅ Run completely automatically
- ✅ Provide professional-quality content

**Welcome to the future of automated blogging!** 🚀

---

*Built with ❤️ | Powered by Azure Functions & Claude AI*