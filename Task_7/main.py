#!/usr/bin/env python3

import os
import json
from datetime import datetime
from typing import List, Dict
from news_scraper import NewsScraper
from deduplicator import NewsDeduplicator
from newsletter_generator import NewsletterGenerator
from telegram_bot import send_newsletter_sync

def save_newsletter(newsletter_content: str, articles: List[Dict]):
    """Save newsletter and articles data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Save newsletter
    with open(f'output/newsletter_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(newsletter_content)
    
    # Save articles data
    with open(f'output/articles_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"Newsletter saved to output/newsletter_{timestamp}.txt")
    print(f"Articles data saved to output/articles_{timestamp}.json")

def main():
    """Main function to run the newsletter generation pipeline"""
    print("🚀 Starting Daily Web3 Newsletter Generation...")
    print("=" * 50)
    
    # Step 1: Scrape news
    print("\n📰 Step 1: Scraping news from sources...")
    scraper = NewsScraper()
    all_articles = scraper.scrape_all_sources()
    
    if not all_articles:
        print("❌ No articles found. Exiting...")
        return
    
    # Step 2: Deduplicate articles
    print("\n🔄 Step 2: Deduplicating articles...")
    deduplicator = NewsDeduplicator()
    unique_articles = deduplicator.deduplicate_articles(all_articles)
    top_articles = deduplicator.get_top_articles(unique_articles)
    
    print(f"✅ Selected {len(top_articles)} top articles")
    
    # Step 3: Generate newsletter
    print("\n📝 Step 3: Generating newsletter content...")
    generator = NewsletterGenerator()
    newsletter_content = generator.create_newsletter(top_articles)
    
    # Step 4: Save newsletter
    print("\n💾 Step 4: Saving newsletter...")
    save_newsletter(newsletter_content, top_articles)
    
    # Step 5: Send to Telegram (optional - only if configured)
    print("\n📱 Step 5: Sending to Telegram...")
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            success = send_newsletter_sync(newsletter_content)
            if success:
                print("✅ Newsletter sent to Telegram successfully!")
            else:
                print("❌ Failed to send newsletter to Telegram")
        else:
            print("⚠️  Telegram not configured. Newsletter saved locally only.")
    except Exception as e:
        print(f"⚠️  Telegram sending failed: {e}")
    
    print("\n✅ Newsletter generation completed!")
    print("=" * 50)
    
    # Display preview
    print("\n📖 Newsletter Preview:")
    print("-" * 30)
    print(newsletter_content[:500] + "..." if len(newsletter_content) > 500 else newsletter_content)

if __name__ == "__main__":
    main()