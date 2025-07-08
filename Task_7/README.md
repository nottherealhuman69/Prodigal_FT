# Task 7: Multi-Agent Newsletter Generator using LangChain

## Overview
This project creates an automated multi-agent system that generates daily Telegram newsletters from top Web3 news sources. The system scrapes news from 5 major publications, deduplicates similar articles, and generates AI-powered summaries using Hugging Face's Mixtral model.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   News Sources  │    │   News Scraper  │    │  Deduplicator   │
│                 │────│                 │────│                 │
│ • CoinDesk      │    │ • Web Scraping  │    │ • Similarity    │
│ • CoinTelegraph │    │ • BeautifulSoup │    │ • TF-IDF        │
│ • Decrypt       │    │ • Rate Limiting │    │ • Cosine Sim    │
│ • Bankless     │    │                 │    │                 │
│ • The Block     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Newsletter Gen  │    │   AI Summary    │    │  Telegram Bot   │
│                 │────│                 │────│                 │
│ • Template      │    │ • Hugging Face  │    │ • Bot API       │
│ • Formatting    │    │ • Mixtral Model │    │ • Message Send  │
│ • Article List  │    │ • Prompt Eng    │    │ • Error Handle  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
Task_7/
├── config.py              # Configuration settings
├── news_scraper.py        # Web scraping module
├── deduplicator.py        # Article deduplication
├── newsletter_generator.py # AI-powered newsletter creation
├── telegram_bot.py        # Telegram bot integration
├── main.py               # Main execution script
├── scheduler.py          # Automated scheduling
├── test_telegram.py      # Telegram bot testing
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
├── demo_script.md       # 5-minute demo script
└── output/              # Generated newsletters
```

## Features

- **Multi-Source Scraping**: Collects news from 5 major Web3 publications
- **Smart Deduplication**: Uses TF-IDF and cosine similarity to remove duplicate articles
- **AI-Powered Summaries**: Leverages Mixtral-8x7B for intelligent content summarization
- **Telegram Integration**: Automatically sends newsletters to Telegram groups
- **Scheduled Execution**: Runs daily at specified times
- **Error Handling**: Robust error handling and fallback mechanisms

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
```

### 3. How to Get Required Tokens

#### Hugging Face API Token:
1. Go to https://huggingface.co/
2. Create account and log in
3. Go to Settings → Access Tokens
4. Create new token with "Read" permissions
5. Copy token to `.env` file

#### Telegram Bot Token:
1. Message @BotFather on Telegram
2. Send `/newbot` command
3. Follow instructions to create bot
4. Copy bot token to `.env` file

#### Telegram Chat ID:
1. Add your bot to a group/channel
2. Send a message to the group
3. Visit: `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
4. Look for "chat":{"id": number
5. Copy chat ID to `.env` file

## How to Run

### Single Run (Generate Newsletter Once)
```bash
python main.py
```

### Test Telegram Connection
```bash
python test_telegram.py
```

### Run Scheduler (Continuous)
```bash
python scheduler.py
```

## How to Know It's Working

### 1. Successful Execution Signs:
- Console shows "🚀 Starting Daily Web3 Newsletter Generation..."
- Articles are scraped from each source (you'll see "Scraping [Source]..." messages)
- Deduplication process shows article count reduction
- AI summary generation completes without errors
- Newsletter files are created in `output/` folder
- If Telegram is configured: "✅ Newsletter sent to Telegram successfully!"

### 2. Output Files:
Check the `output/` folder for:
- `newsletter_YYYYMMDD_HHMMSS.txt` - Generated newsletter
- `articles_YYYYMMDD_HHMMSS.json` - Raw article data

### 3. Console Output Example:
```
🚀 Starting Daily Web3 Newsletter Generation...
==================================================

📰 Step 1: Scraping news from sources...
Scraping CoinDesk...
Scraping CoinTelegraph...
Scraping Decrypt...
Scraping Bankless...
Scraping The Block...
Total articles scraped: 25

🔄 Step 2: Deduplicating articles...
Deduplicated: 25 -> 18 articles
✅ Selected 10 top articles

📝 Step 3: Generating newsletter content...

💾 Step 4: Saving newsletter...
Newsletter saved to output/newsletter_20250706_143022.txt
Articles data saved to output/articles_20250706_143022.json

📱 Step 5: Sending to Telegram...
✅ Newsletter sent to Telegram successfully!

✅ Newsletter generation completed!
```

### 4. Troubleshooting:

#### If scraping fails:
- Check internet connection
- Some sites may have anti-bot protection
- Script will continue with available articles

#### If AI summary fails:
- Check Hugging Face API token
- Fallback generic summary will be used
- Newsletter generation continues

#### If Telegram fails:
- Run `python test_telegram.py` to diagnose
- Check bot token and chat ID
- Ensure bot is added to the group
- Newsletter is still saved locally

## Demo Flow

### Quick Test (2 minutes):
```bash
# 1. Install and configure
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your tokens

# 2. Test components
python test_telegram.py

# 3. Generate newsletter
python main.py
```

### Scheduled Demo (5 minutes):
```bash
# Run scheduler (generates every 2 minutes for demo)
python scheduler.py
```

## File Descriptions

- **config.py**: Central configuration with API keys, model settings, and news sources
- **news_scraper.py**: Web scraping logic for each news source with error handling
- **deduplicator.py**: TF-IDF based similarity detection and article ranking
- **newsletter_generator.py**: AI-powered content generation using Hugging Face API
- **telegram_bot.py**: Async Telegram bot with message chunking for long newsletters
- **main.py**: Main orchestration script that ties all components together
- **scheduler.py**: Automated daily execution with configurable timing
- **test_telegram.py**: Standalone Telegram bot testing utility

## Key Features Implemented

✅ **Multi-Source Scraping**: CoinDesk, CoinTelegraph, Decrypt, Bankless, The Block  
✅ **Deduplication**: Cosine similarity using TF-IDF vectors  
✅ **Top Article Selection**: Priority-based ranking system  
✅ **AI Summary Generation**: Hugging Face Mixtral-8x7B integration  
✅ **Newsletter Composition**: Structured format with header, body, footer  
✅ **Telegram Automation**: Daily newsletter delivery to groups  
✅ **Scheduling**: Automated 2+ days simulation capability  
✅ **Error Handling**: Graceful fallbacks for each component  
✅ **Local Storage**: JSON and text file outputs for backup  

## Technical Notes

- **Rate Limiting**: 2-second delays between source scraping
- **Message Limits**: Telegram messages split at 4000 characters
- **Similarity Threshold**: 0.8 cosine similarity for duplicate detection
- **Max Articles**: Limited to top 10 articles per newsletter
- **Fallback Mechanisms**: Generic summaries if AI fails, local storage if Telegram fails

## Sample Output Structure

```
🚀 Daily Web3 Newsletter - July 06, 2025

📊 Today's Summary:
[AI-generated summary of key trends and developments]

📰 Top Stories:

1. Bitcoin Reaches New All-Time High
🔗 Source: CoinDesk
📖 Bitcoin price surges past $100,000 mark amid institutional adoption...
🌐 Link: https://coindesk.com/...

[... more articles ...]

---
🔔 Stay updated with the latest Web3 news!
📱 Follow us for daily crypto insights.
```