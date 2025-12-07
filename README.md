<div align="center">

# 🚀 n8n Workflow Collection

[![n8n](https://img.shields.io/badge/n8n-Automation-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Projects](https://img.shields.io/badge/Projects-2-blue?style=for-the-badge)](#-projects)
[![AI Powered](https://img.shields.io/badge/AI-Powered-orange?style=for-the-badge&logo=openai&logoColor=white)](#)

**Production-ready n8n workflows for stock analysis and viral marketing automation**

[View Projects](#-projects) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack) • [Documentation](#-documentation)

</div>

---

## 📋 Overview

This repository contains battle-tested n8n workflows designed for real-world automation scenarios. Each project includes comprehensive documentation, setup guides, and workflow JSON files ready for import.

### 🎯 What's Inside

- **Automated Stock Analysis** - Real-time stock tracking with AI-powered insights
- **Viral Marketing Engine** - TikTok trend analysis and creator settlement automation
- **Production-Ready** - Tested workflows with error handling and monitoring
- **AI Integration** - GPT-4 powered analysis and decision-making

---

## 🗂️ Projects

<table>
<tr>
<td width="50%">

### 📊 Stock Tracking System

![Status](https://img.shields.io/badge/Status-Production-success?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0-blue?style=flat-square)

**Automated stock analysis pipeline with multi-source data collection**

#### Key Features
- 🇺🇸 US Stock data via Alpha Vantage
- 🇰🇷 Korean Stock data via KIS Developers
- 📈 Technical indicators (RSI, MACD, Bollinger Bands)
- 💡 AI-powered investment insights (GPT-4)
- 📱 Telegram notifications
- 🔄 Automated 2-hour intervals

#### Tech Stack
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

[📖 Documentation](./stock-tracking/README.md) • [⚡ Quick Setup](#stock-tracking-setup)

</td>
<td width="50%">

### 🎬 Virality - TikTok Marketing Automation

![Status](https://img.shields.io/badge/Status-Paused-yellow?style=flat-square)
![Progress](https://img.shields.io/badge/Progress-80%25-orange?style=flat-square)

**AI-driven viral marketing lifecycle automation for TikTok creators**

#### Key Features
- 📊 Daily trend analysis & Blue Ocean detection
- 💰 Dynamic creator settlement system
- 🛡️ AI Fraud Detection System (FDS)
- 🧪 A/B Testing automation
- 📈 Weekly business review reports
- 🔔 Slack notifications

#### Tech Stack
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-4A154B?style=flat-square&logo=slack&logoColor=white)
![TikTok](https://img.shields.io/badge/TikTok-000000?style=flat-square&logo=tiktok&logoColor=white)

**⚠️ Blocked**: TikTok Advertising Account approval pending

[📖 Documentation](./virality/README.md) • [🔍 View Architecture](./virality/WorkflowStructure.png)

</td>
</tr>
</table>

---

## 🛠️ Tech Stack

<div align="center">

### Core Platform
![n8n](https://img.shields.io/badge/n8n-v1.0+-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### AI & APIs
![OpenAI](https://img.shields.io/badge/OpenAI_GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white)
![Alpha Vantage](https://img.shields.io/badge/Alpha_Vantage-0055FF?style=for-the-badge)
![TikTok API](https://img.shields.io/badge/TikTok_API-000000?style=for-the-badge&logo=tiktok&logoColor=white)

### Development
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

### Notifications
![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)

</div>

---

## 🚀 Quick Start

### Prerequisites

```bash
# Docker & Docker Compose
docker --version  # >= 20.10
docker-compose --version  # >= 1.29

# n8n (if running locally)
npm install n8n -g
```

### Installation

```bash
# 1. Clone repository
git clone https://github.com/tygwan/n8n.git
cd n8n

# 2. Choose a project
cd stock-tracking  # or cd virality

# 3. Import workflows to n8n
# n8n UI → Workflows → Import from File → Select JSON files

# 4. Configure API keys
# See API_SETUP_GUIDE.md for detailed instructions
```

### Stock Tracking Setup

```bash
cd stock-tracking

# 1. Import workflows in order:
#    - US_Stock_Data_Collector.json
#    - KR_Stock_Data_Collector.json
#    - Stock_Analysis_Engine.json
#    - Main_Stock_Orchestrator.json

# 2. Set environment variables (see API_SETUP_GUIDE.md)

# 3. Configure Telegram bot
#    - Get bot token from @BotFather
#    - Update Main_Stock_Orchestrator workflow

# 4. Activate Main_Stock_Orchestrator
```

### Virality Setup

```bash
cd virality

# Import workflow
n8n import:workflow --input=workflows/virality_full_workflow.json

# Configure credentials (see SETUP_GUIDE.md)

# ⚠️ Note: TikTok API access required
```

---

## 📁 Repository Structure

```
n8n/
├── stock-tracking/          # Stock analysis automation
│   ├── README.md           # Detailed documentation
│   ├── workflow/           # n8n workflow JSON files
│   └── telegram_collector/ # Python data collector
│
├── virality/               # TikTok marketing automation
│   ├── README.md          # Project overview
│   ├── SETUP_GUIDE.md     # Setup instructions
│   ├── workflows/         # n8n workflow JSON files
│   └── *.png              # Architecture diagrams
│
├── .gitignore             # Security: excludes sensitive files
├── API_SETUP_GUIDE.md     # API key setup (LOCAL ONLY)
└── README.md              # This file
```

---

## 🔐 Security

**⚠️ IMPORTANT**: This repository does NOT contain:
- API keys or secrets
- `.env` files
- Authentication tokens
- Personal credentials

All sensitive information is:
- ✅ Excluded via `.gitignore`
- ✅ Documented in `API_SETUP_GUIDE.md` (local only)
- ✅ Configured through n8n credentials UI

**Before committing**, always verify:
```bash
git status  # Check for sensitive files
grep -r "api_key\|secret\|token" --exclude-dir=.git
```

---

## 📊 Features Comparison

| Feature | Stock Tracking | Virality |
|---------|---------------|----------|
| **AI Analysis** | ✅ GPT-4 | ✅ GPT-4 |
| **Automation** | ✅ Scheduled | ✅ Event-driven |
| **Data Collection** | ✅ Multi-source | ✅ TikTok API |
| **Notifications** | ✅ Telegram | ✅ Slack |
| **Status** | 🟢 Production | 🟡 Paused (API approval) |
| **Complexity** | Medium | High |

---

## 📖 Documentation

Each project includes comprehensive documentation:

### Stock Tracking
- [README.md](./stock-tracking/README.md) - Full documentation
- Architecture diagrams
- API integration guides
- Customization tips

### Virality
- [README.md](./virality/README.md) - Project overview
- [SETUP_GUIDE.md](./virality/SETUP_GUIDE.md) - Installation
- [IMPLEMENTATION_GUIDE.md](./virality/IMPLEMENTATION_GUIDE.md) - Technical details
- [PORTFOLIO.md](./virality/PORTFOLIO.md) - Portfolio showcase

---

## ⚠️ Disclaimer

- **Not Financial Advice**: Stock analysis results are for reference only
- **API Limits**: Free API tiers have rate limits (caching recommended)
- **Compliance**: Use for personal, non-commercial purposes only
- **Testing**: Always test workflows in development environment first

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🔗 Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [Workflow Templates](https://n8n.io/workflows/)
- [API Setup Guide](./API_SETUP_GUIDE.md) *(local only)*

---

<div align="center">

**Built with** ❤️ **using n8n + AI**

[![GitHub](https://img.shields.io/badge/GitHub-tygwan-181717?style=for-the-badge&logo=github)](https://github.com/tygwan)

*Last Updated: December 2024*

</div>
