import os
from dotenv import load_dotenv

load_dotenv()

# API Keys and Tokens
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')

# Model Configuration
MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# News Sources
NEWS_SOURCES = {
    'coindesk': 'https://www.coindesk.com/news/',
    'cointelegraph': 'https://cointelegraph.com/news',
    'decrypt': 'https://decrypt.co/news',
    'bankless': 'https://www.bankless.com/',
    'theblock': 'https://www.theblock.co/latest'
}

# Newsletter Configuration
MAX_ARTICLES = 10
SIMILARITY_THRESHOLD = 0.8