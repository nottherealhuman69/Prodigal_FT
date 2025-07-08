# langchain_agents.py - Fixed version with better error handling

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
import json
from datetime import datetime

# Pydantic Models for Validation
class Article(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    link: str = Field(..., min_length=10)
    source: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    scraped_at: Optional[str] = None
    
    @validator('link')
    def validate_link(cls, v):
        if not (v.startswith('http://') or v.startswith('https://')):
            # Allow relative URLs, we'll fix them later
            pass
        return v

class Newsletter(BaseModel):
    title: str = Field(..., min_length=10)
    summary: str = Field(..., min_length=50)
    articles: List[Article] = Field(..., min_items=1, max_items=10)
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @validator('articles')
    def validate_articles(cls, v):
        if len(set(article.title for article in v)) != len(v):
            raise ValueError('Articles must have unique titles')
        return v

# Simplified Agents (without LangChain dependency issues)
class ScrapingAgent:
    """Agent responsible for web scraping coordination"""
    
    def __init__(self):
        self.name = "ScrapingAgent"
    
    def scrape_sources(self, sources: List[str] = None) -> str:
        """Tool function for scraping news sources"""
        try:
            from news_scraper import NewsScraper
            
            scraper = NewsScraper()
            articles = scraper.scrape_all_sources()
            
            # Validate articles with more lenient validation
            validated_articles = []
            for article_data in articles:
                try:
                    # Add default description if missing
                    if 'description' not in article_data or len(article_data['description']) < 10:
                        article_data['description'] = article_data['title'][:100] + '...'
                    
                    article = Article(**article_data)
                    validated_articles.append(article.dict())
                except Exception as e:
                    print(f"  Warning: Skipping invalid article: {e}")
                    continue
            
            return json.dumps({
                "status": "success",
                "article_count": len(validated_articles),
                "articles": validated_articles
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

class AnalysisAgent:
    """Agent responsible for article analysis and deduplication"""
    
    def __init__(self):
        self.name = "AnalysisAgent"
    
    def deduplicate_articles(self, articles_json: str) -> str:
        """Tool function for article deduplication"""
        try:
            from deduplicator import NewsDeduplicator
            
            articles_data = json.loads(articles_json)
            articles = articles_data.get("articles", [])
            
            # Validate articles
            validated_articles = []
            for article_data in articles:
                try:
                    article = Article(**article_data)
                    validated_articles.append(article.dict())
                except Exception:
                    continue
            
            deduplicator = NewsDeduplicator()
            unique_articles = deduplicator.deduplicate_articles(validated_articles)
            top_articles = deduplicator.get_top_articles(unique_articles)
            
            return json.dumps({
                "status": "success",
                "original_count": len(validated_articles),
                "deduplicated_count": len(unique_articles),
                "final_count": len(top_articles),
                "articles": top_articles
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

class ContentAgent:
    """Agent responsible for content generation"""
    
    def __init__(self):
        self.name = "ContentAgent"
    
    def generate_newsletter(self, articles_json: str) -> str:
        """Tool function for newsletter generation - no external API dependencies"""
        try:
            articles_data = json.loads(articles_json)
            articles = articles_data.get("articles", [])
            
            # Validate articles
            validated_articles = []
            for article_data in articles:
                try:
                    article = Article(**article_data)
                    validated_articles.append(article.dict())
                except Exception:
                    continue
            
            if not validated_articles:
                raise ValueError("No valid articles to process")
            
            # Generate newsletter without external API
            today = datetime.now().strftime("%B %d, %Y")
            
            # Create simple but effective summary
            sources = list(set([article.get('source', 'Unknown') for article in validated_articles]))
            summary = f"Today's Web3 newsletter covers {len(validated_articles)} key stories from {len(sources)} major publications. "
            summary += "Key developments include cryptocurrency market movements, blockchain technology updates, DeFi innovations, and regulatory news shaping the digital asset landscape."
            
            # Build newsletter
            newsletter_content = f"""🚀 **Daily Web3 Newsletter - {today}**

📊 **Today's Summary:**
{summary}

📰 **Top Stories:**

"""
            
            # Add articles
            for i, article in enumerate(validated_articles, 1):
                newsletter_content += f"""**{i}. {article['title']}**
🔗 Source: {article['source']}
📖 {article['description']}
🌐 Link: {article['link']}

"""
            
            # Footer
            newsletter_content += """---
🔔 Stay updated with the latest Web3 news!
📱 Follow us for daily crypto insights.

*This newsletter is automatically generated using LangChain multi-agent AI system.*
"""
            
            # Validate newsletter structure
            newsletter = Newsletter(
                title=f"Daily Web3 Newsletter - {today}",
                summary=summary,
                articles=[Article(**article) for article in validated_articles]
            )
            
            return json.dumps({
                "status": "success",
                "newsletter": newsletter_content,
                "metadata": newsletter.dict()
            })
        except Exception as e:
            print(f"Content generation error: {e}")
            return json.dumps({"status": "error", "message": str(e)})

class DeliveryAgent:
    """Agent responsible for newsletter delivery"""
    
    def __init__(self):
        self.name = "DeliveryAgent"
    
    def send_telegram(self, newsletter_json: str) -> str:
        """Tool function for Telegram delivery"""
        try:
            from telegram_bot import send_newsletter_sync
            
            newsletter_data = json.loads(newsletter_json)
            newsletter_content = newsletter_data.get("newsletter", "")
            
            if not newsletter_content:
                raise ValueError("No newsletter content to send")
            
            success = send_newsletter_sync(newsletter_content)
            
            return json.dumps({
                "status": "success" if success else "failed",
                "message": "Newsletter delivered successfully" if success else "Delivery failed"
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

class NewsletterOrchestrator:
    """Simplified orchestrator without complex LangChain dependencies"""
    
    def __init__(self):
        # Initialize agents
        self.scraping_agent = ScrapingAgent()
        self.analysis_agent = AnalysisAgent()
        self.content_agent = ContentAgent()
        self.delivery_agent = DeliveryAgent()
    
    def generate_newsletter_with_agents(self):
        """Generate newsletter using multi-agent system"""
        print("🤖 Starting Multi-Agent Newsletter Generation...")
        
        try:
            # Step 1: Scraping
            print("📰 Agent 1: Scraping news sources...")
            scraping_result = self.scraping_agent.scrape_sources([])
            scraping_data = json.loads(scraping_result)
            
            if scraping_data["status"] != "success":
                raise Exception(f"Scraping failed: {scraping_data.get('message', 'Unknown error')}")
            
            print(f"✅ Scraped {scraping_data['article_count']} articles")
            
            # Step 2: Analysis 
            print("🔄 Agent 2: Analyzing and deduplicating...")
            analysis_result = self.analysis_agent.deduplicate_articles(scraping_result)
            analysis_data = json.loads(analysis_result)
            
            if analysis_data["status"] != "success":
                raise Exception(f"Analysis failed: {analysis_data.get('message', 'Unknown error')}")
            
            print(f"✅ Deduplicated to {analysis_data['final_count']} articles")
            
            # Step 3: Content Generation
            print("📝 Agent 3: Generating newsletter content...")
            content_result = self.content_agent.generate_newsletter(analysis_result)
            content_data = json.loads(content_result)
            
            if content_data["status"] != "success":
                raise Exception(f"Content generation failed: {content_data.get('message', 'Unknown error')}")
            
            print("✅ Newsletter content generated")
            
            # Step 4: Delivery
            print("📱 Agent 4: Delivering via Telegram...")
            delivery_result = self.delivery_agent.send_telegram(content_result)
            delivery_data = json.loads(delivery_result)
            
            if delivery_data["status"] == "success":
                print("✅ Newsletter delivered successfully!")
            else:
                print("⚠️ Newsletter saved locally, Telegram delivery failed")
            
            return content_data["newsletter"]
            
        except Exception as e:
            print(f"❌ Multi-agent generation failed: {e}")
            return None

# Simple function for direct execution
def run_langchain_newsletter():
    """Run newsletter generation with multi-agent system"""
    orchestrator = NewsletterOrchestrator()
    return orchestrator.generate_newsletter_with_agents()

if __name__ == "__main__":
    run_langchain_newsletter()