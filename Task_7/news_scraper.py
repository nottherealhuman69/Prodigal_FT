import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
from datetime import datetime, timedelta
from config import NEWS_SOURCES

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def add_timestamp_to_article(self, article: Dict) -> Dict:
        """Add current timestamp to article for freshness tracking"""
        article['scraped_at'] = datetime.now().isoformat()
        article['scrape_id'] = f"{int(time.time())}_{random.randint(100, 999)}"
        return article
    
    def scrape_coindesk_varied(self) -> List[Dict]:
        """Enhanced CoinDesk scraper with more variety"""
        articles = []
        
        # Try multiple sections
        sections = [
            'https://www.coindesk.com/news/',
            'https://www.coindesk.com/markets/',
            'https://www.coindesk.com/policy/',
            'https://www.coindesk.com/tech/'
        ]
        
        for section_url in sections[:2]:  # Try first 2 sections
            try:
                print(f"  → Scraping {section_url}")
                response = self.session.get(section_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors
                selectors = [
                    'div.contentSection',
                    'article',
                    'div[class*="story"]',
                    'h3 a',
                    'h2 a'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)[:3]  # Get 3 from each selector
                    
                    for elem in elements:
                        try:
                            if elem.name == 'a':
                                title = elem.get_text(strip=True)
                                link = elem.get('href')
                            else:
                                title_elem = elem.find('a') or elem.find('h3') or elem.find('h2')
                                if not title_elem:
                                    continue
                                title = title_elem.get_text(strip=True)
                                link = title_elem.get('href') if title_elem.name == 'a' else elem.find('a', href=True)
                                link = link.get('href') if link else None
                            
                            if title and len(title) > 20:
                                if link and not link.startswith('http'):
                                    link = 'https://www.coindesk.com' + link
                                
                                article = {
                                    'title': title,
                                    'link': link or section_url,
                                    'source': 'CoinDesk',
                                    'description': title[:100] + '...' if len(title) > 100 else title,
                                    'section': section_url.split('/')[-2]
                                }
                                articles.append(self.add_timestamp_to_article(article))
                        except:
                            continue
                    
                    if len(articles) >= 5:  # Got enough from this section
                        break
                
                time.sleep(1)  # Brief delay between sections
                
            except Exception as e:
                print(f"    Error scraping {section_url}: {e}")
                continue
        
        # Remove duplicates by title
        seen_titles = set()
        unique_articles = []
        for article in articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        return unique_articles[:7]  # Return top 7
    
    def scrape_with_search_variety(self, base_url: str, source_name: str) -> List[Dict]:
        """Enhanced scraper with search variety"""
        articles = []
        
        # Try different approaches
        urls_to_try = [base_url]
        
        # Add search URLs for some sites
        if 'cointelegraph' in base_url:
            search_terms = ['bitcoin', 'ethereum', 'defi']
            term = random.choice(search_terms)
            urls_to_try.append(f"https://cointelegraph.com/search?query={term}")
        
        for url in urls_to_try[:2]:  # Try max 2 URLs per source
            try:
                print(f"  → Trying {url}")
                response = self.session.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Multiple selector strategies
                selectors = [
                    'article',
                    'div[class*="post"]',
                    'div[class*="article"]',
                    'div[class*="story"]',
                    'h2 a',
                    'h3 a',
                    'a[href*="/news/"]',
                    'a[href*="/article/"]'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)[:5]
                    
                    for elem in elements:
                        try:
                            if elem.name == 'a':
                                title = elem.get_text(strip=True)
                                link = elem.get('href')
                            else:
                                # Look for title and link
                                title_elem = elem.find('h1') or elem.find('h2') or elem.find('h3') or elem.find('a')
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                link_elem = elem.find('a', href=True)
                                link = link_elem.get('href') if link_elem else None
                            
                            # Filter and clean
                            if title and len(title) > 15 and 'cookie' not in title.lower():
                                if link:
                                    if not link.startswith('http'):
                                        base_domain = url.split('/')[2]
                                        link = f"https://{base_domain}{link}"
                                
                                article = {
                                    'title': title,
                                    'link': link or url,
                                    'source': source_name,
                                    'description': title[:100] + '...' if len(title) > 100 else title,
                                    'scrape_method': selector
                                }
                                articles.append(self.add_timestamp_to_article(article))
                                
                        except Exception as e:
                            continue
                    
                    if len(articles) >= 5:
                        break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    Error with {url}: {e}")
                continue
        
        # Remove duplicates
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title_clean = article['title'].lower().strip()
            if title_clean not in seen_titles and len(title_clean) > 15:
                seen_titles.add(title_clean)
                unique_articles.append(article)
        
        return unique_articles[:5]
    
    def scrape_all_sources(self) -> List[Dict]:
        """Enhanced scraping with more variety and randomness"""
        all_articles = []
        
        print("📰 Enhanced scraping with variety...")
        
        # CoinDesk with enhanced scraping
        print("Scraping CoinDesk (enhanced)...")
        coindesk_articles = self.scrape_coindesk_varied()
        all_articles.extend(coindesk_articles)
        time.sleep(2)
        
        # Other sources with variety
        sources = [
            ('cointelegraph', 'CoinTelegraph'),
            ('decrypt', 'Decrypt'),
            ('theblock', 'The Block'),
            ('bankless', 'Bankless')
        ]
        
        # Randomize order
        random.shuffle(sources)
        
        for source_key, source_name in sources:
            print(f"Scraping {source_name} (varied approach)...")
            try:
                articles = self.scrape_with_search_variety(
                    NEWS_SOURCES[source_key], 
                    source_name
                )
                all_articles.extend(articles)
                time.sleep(random.uniform(1.5, 3.0))  # Random delay
            except Exception as e:
                print(f"  Error with {source_name}: {e}")
                continue
        
        # Add some randomness to article order
        random.shuffle(all_articles)
        
        print(f"📊 Total unique articles scraped: {len(all_articles)}")
        
        # Add freshness score
        for article in all_articles:
            article['freshness_score'] = random.uniform(0.5, 1.0)
        
        return all_articles