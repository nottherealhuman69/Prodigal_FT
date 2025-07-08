# Task 7: Multi-Agent Newsletter Generator using LangChain

## Overview
An automated multi-agent system that scrapes Web3 news from top publications, deduplicates articles, generates newsletters, and delivers them via Telegram using LangChain agents.

## Architecture

### System Flow Diagram
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ Scraping    │───▶│ Analysis     │───▶│ Content     │───▶│ Delivery     │
│ Agent       │    │ Agent        │    │ Agent       │    │ Agent        │
│             │    │              │    │             │    │              │
│ • CoinDesk  │    │ • Dedup      │    │ • Summary   │    │ • Telegram   │
│ • CoinTele  │    │ • Similarity │    │ • Format    │    │ • Schedule   │
│ • Decrypt   │    │ • Top 10     │    │ • Template  │    │ • Error      │
│ • Bankless │    │ • Filter     │    │ • AI Gen    │    │   Handling   │
│ • TheBlock  │    │              │    │             │    │              │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
```

### Multi-Agent Architecture
1. **ScrapingAgent**: Coordinates web scraping from 5 news sources
2. **AnalysisAgent**: Handles deduplication using cosine similarity
3. **ContentAgent**: Generates newsletter content with AI summaries
4. **DeliveryAgent**: Manages Telegram delivery and error handling

## Features
- ✅ Scrapes 5 major Web3 publications
- ✅ LangChain multi-agent orchestration
- ✅ Cosine similarity deduplication
- ✅ Top 10 article selection
- ✅ AI-generated summaries (Hugging Face)
- ✅ Automated scheduling (daily + demo mode)
- ✅ Telegram bot integration
- ✅ Pydantic validation
- ✅ Error handling and fallbacks

## Setup Instructions

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd task7-newsletter-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Hugging Face API (for AI summaries)
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

### 3. Getting API Keys

#### Telegram Bot Setup:
1. Message @BotFather on Telegram
2. Create a new bot: `/newbot`
3. Get your bot token
4. Add bot to your group/channel
5. Get chat ID using: `https://api.telegram.org/bot<TOKEN>/getUpdates`

#### Hugging Face Token:
1. Sign up at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create a new token

## Running the Application

### Manual Execution
```bash
# Run once manually
python main.py

# Test Telegram connection
python test_telegram.py
```

### Scheduled Execution
```bash
# Run scheduler (daily at 9 AM + every 2 minutes for demo)
python scheduler.py
```

### LangChain Multi-Agent Mode
```bash
# Run with LangChain agents
python langchain_agents.py
```

## File Structure
```
task7-newsletter-generator/
├── README.md                 # This file
├── SUMMARY.md                # Challenges and decisions
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── config.py                # Configuration management
├── main.py                  # Main orchestrator
├── news_scraper.py          # Web scraping logic
├── deduplicator.py          # Similarity detection
├── newsletter_generator.py  # Content generation
├── langchain_agents.py      # Multi-agent system
├── telegram_bot.py          # Telegram integration
├── scheduler.py             # Automation scheduler
├── test_telegram.py         # Telegram testing
└── output/                  # Generated newsletters
    ├── newsletter_YYYYMMDD_HHMMSS.txt
    └── articles_YYYYMMDD_HHMMSS.json
```

## Data Sources
1. **CoinDesk** - https://www.coindesk.com/news/
2. **CoinTelegraph** - https://cointelegraph.com/news
3. **Decrypt** - https://decrypt.co/news
4. **Bankless** - https://www.bankless.com/
5. **The Block** - https://www.theblock.co/latest

## Output Example
```
🚀 Daily Web3 Newsletter - January 15, 2025

📊 Today's Summary:
Today's Web3 newsletter covers 8 key stories from 4 major publications...

📰 Top Stories:

1. Bitcoin Reaches New All-Time High Above $100K
🔗 Source: CoinDesk
📖 Bitcoin surpassed $100,000 for the first time...
🌐 Link: https://www.coindesk.com/...

[Additional articles...]
```

## Testing
```bash
# Test individual components
python -c "from news_scraper import NewsScraper; print(len(NewsScraper().scrape_all_sources()))"
python -c "from telegram_bot import send_newsletter_sync; send_newsletter_sync('Test message')"

# Test full pipeline
python main.py
```

## Troubleshooting

### Common Issues:
1. **Scraping failures**: Some sites may block requests - implemented retry logic
2. **Telegram errors**: Check bot permissions and chat ID
3. **API rate limits**: Hugging Face has rate limits - fallback to simple summaries
4. **Network timeouts**: Implemented timeout handling and retries

### Debug Mode:
```bash
# Enable verbose logging
export DEBUG=1
python main.py
```

## Performance
- **Scraping**: ~30-60 seconds for all sources
- **Deduplication**: <5 seconds for 50 articles
- **Newsletter generation**: <10 seconds
- **Total runtime**: ~2-3 minutes end-to-end

## Next Steps for Production
1. Add database persistence (PostgreSQL)
2. Implement Redis caching
3. Add monitoring and alerting
4. Scale with containerization
5. Add more sophisticated ML models
6. Implement user feedback loop