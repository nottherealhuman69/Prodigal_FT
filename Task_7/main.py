#!/usr/bin/env python3

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict

def load_previous_articles() -> set:
    """Load previously sent article titles to avoid duplicates"""
    try:
        if os.path.exists('previous_articles.json'):
            with open('previous_articles.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('titles', []))
    except:
        pass
    return set()

def save_current_articles(articles: List[Dict]):
    """Save current article titles for next run"""
    try:
        titles = [article['title'] for article in articles]
        with open('previous_articles.json', 'w', encoding='utf-8') as f:
            json.dump({
                'titles': titles,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save article history: {e}")

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

def main_with_langchain():
    """Main function using LangChain multi-agent system"""
    print("🚀 Starting LangChain Multi-Agent Newsletter Generation...")
    print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Try to use LangChain agents first
        from langchain_agents import run_langchain_newsletter
        
        print("\n🤖 Using LangChain Multi-Agent System...")
        newsletter_content = run_langchain_newsletter()
        
        if newsletter_content:
            print("\n💾 Saving LangChain generated newsletter...")
            # Extract articles for saving (simplified for demo)
            dummy_articles = [{"title": "LangChain Generated Newsletter", "source": "Multi-Agent System"}]
            save_newsletter(newsletter_content, dummy_articles)
            save_current_articles(dummy_articles)
            
            print("✅ LangChain newsletter generation completed!")
            return
            
    except ImportError:
        print("⚠️ LangChain not available, falling back to standard pipeline...")
    except Exception as e:
        print(f"⚠️ LangChain generation failed: {e}")
        print("🔄 Falling back to standard pipeline...")
    
    # Fallback to original implementation
    main_standard()

def main_standard():
    """Original main function implementation"""
    from news_scraper import NewsScraper
    from deduplicator import NewsDeduplicator
    from newsletter_generator import NewsletterGenerator
    from telegram_bot import send_newsletter_sync
    
    print("\n📰 Using Standard Pipeline...")
    
    # Load previous articles to avoid repeats
    print("\n🔍 Checking for previous articles...")
    previous_titles = load_previous_articles()
    print(f"📚 Found {len(previous_titles)} previously processed articles")
    
    # Step 1: Scrape news
    print("\n📰 Step 1: Scraping news from sources...")
    scraper = NewsScraper()
    all_articles = scraper.scrape_all_sources()
    
    if not all_articles:
        print("❌ No articles found. Exiting...")
        return
    
    # Filter new articles
    new_articles = []
    for article in all_articles:
        if article['title'] not in previous_titles:
            new_articles.append(article)
    
    print(f"📊 Filtered: {len(all_articles)} total → {len(new_articles)} new articles")
    
    if len(new_articles) < 3:
        print("⚠️  Very few new articles found. Including some previous articles for content.")
        new_articles = all_articles[:max(10, len(new_articles))]
    
    # Step 2: Deduplicate articles
    print("\n🔄 Step 2: Deduplicating articles...")
    deduplicator = NewsDeduplicator()
    unique_articles = deduplicator.deduplicate_articles(new_articles)
    top_articles = deduplicator.get_top_articles(unique_articles)
    
    print(f"✅ Selected {len(top_articles)} top articles")
    
    if len(top_articles) == 0:
        print("❌ No articles to process. Exiting...")
        return
    
    # Step 3: Generate newsletter
    print("\n📝 Step 3: Generating newsletter content...")
    generator = NewsletterGenerator()
    newsletter_content = generator.create_newsletter(top_articles)
    
    # Add time context
    current_time = datetime.now()
    time_context = f"Generated at {current_time.strftime('%H:%M')} on {current_time.strftime('%B %d, %Y')}"
    newsletter_content += f"\n\n⏰ {time_context}\n🔄 Run #{hash(str(current_time)) % 1000:03d}"
    
    # Step 4: Save newsletter
    print("\n💾 Step 4: Saving newsletter...")
    save_newsletter(newsletter_content, top_articles)
    save_current_articles(top_articles)
    
    # Step 5: Send to Telegram
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
    
    print(f"\n✅ Newsletter generation completed!")
    print(f"📊 Stats: {len(all_articles)} scraped → {len(new_articles)} new → {len(top_articles)} selected")
    print("=" * 50)
    
    # Display preview
    print("\n📖 Newsletter Preview:")
    print("-" * 30)
    preview = newsletter_content[:500] + "..." if len(newsletter_content) > 500 else newsletter_content
    print(preview)

def main():
    """Main entry point - try LangChain first, fallback to standard"""
    try:
        main_with_langchain()
    except Exception as e:
        print(f"Error in main execution: {e}")
        print("Falling back to standard implementation...")
        main_standard()

if __name__ == "__main__":
    main()