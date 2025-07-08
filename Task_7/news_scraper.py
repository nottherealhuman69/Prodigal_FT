import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from config import NEWS_SOURCES

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_coindesk(self) -> List[Dict]:
        """Scrape CoinDesk news"""
        try:
            response = requests.get(NEWS_SOURCES['coindesk'], headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            # Find article containers
            article_elements = soup.find_all('div', class_='contentSection')[:5]  # Get top 5
            
            for article in article_elements:
                try:
                    title_elem = article.find('h3') or article.find('h2')
                    link_elem = article.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get('href')
                        if link and not link.startswith('http'):
                            link = 'https://www.coindesk.com' + link
                        
                        articles.append({
                            'title': title,
                            'link': link,
                            'source': 'CoinDesk',
                            'description': title[:100] + '...' if len(title) > 100 else title
                        })
                except:
                    continue
            
            return articles
        except Exception as e:
            print(f"Error scraping CoinDesk: {e}")
            return []
    
    def scrape_cointelegraph(self) -> List[Dict]:
        """Scrape CoinTelegraph news"""
        try:
            response = requests.get(NEWS_SOURCES['cointelegraph'], headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            # Find article containers
            article_elements = soup.find_all('article')[:5]  # Get top 5
            
            for article in article_elements:
                try:
                    title_elem = article.find('h2') or article.find('h3')
                    link_elem = article.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get('href')
                        if link and not link.startswith('http'):
                            link = 'https://cointelegraph.com' + link
                        
                        articles.append({
                            'title': title,
                            'link': link,
                            'source': 'CoinTelegraph',
                            'description': title[:100] + '...' if len(title) > 100 else title
                        })
                except:
                    continue
            
            return articles
        except Exception as e:
            print(f"Error scraping CoinTelegraph: {e}")
            return []
    
    def scrape_basic_news(self, source_name: str, url: str) -> List[Dict]:
        """Basic scraper for other news sources"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            # Try to find common article patterns
            selectors = ['article', 'div[class*="post"]', 'div[class*="article"]', 'h2', 'h3']
            
            for selector in selectors:
                elements = soup.select(selector)[:5]
                for elem in elements:
                    try:
                        title_elem = elem.find('a') or elem
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get('href') if title_elem.name == 'a' else None
                            
                            if title and len(title) > 20:  # Filter out short titles
                                if link and not link.startswith('http'):
                                    link = url + link
                                
                                articles.append({
                                    'title': title,
                                    'link': link or url,
                                    'source': source_name,
                                    'description': title[:100] + '...' if len(title) > 100 else title
                                })
                    except:
                        continue
                
                if articles:  # If we found articles, break
                    break
            
            return articles[:5]  # Return top 5
        except Exception as e:
            print(f"Error scraping {source_name}: {e}")
            return []
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all news sources"""
        all_articles = []
        
        print("Scraping CoinDesk...")
        all_articles.extend(self.scrape_coindesk())
        time.sleep(2)
        
        print("Scraping CoinTelegraph...")
        all_articles.extend(self.scrape_cointelegraph())
        time.sleep(2)
        
        print("Scraping Decrypt...")
        all_articles.extend(self.scrape_basic_news('Decrypt', NEWS_SOURCES['decrypt']))
        time.sleep(2)
        
        print("Scraping Bankless...")
        all_articles.extend(self.scrape_basic_news('Bankless', NEWS_SOURCES['bankless']))
        time.sleep(2)
        
        print("Scraping The Block...")
        all_articles.extend(self.scrape_basic_news('The Block', NEWS_SOURCES['theblock']))
        
        print(f"Total articles scraped: {len(all_articles)}")
        return all_articles