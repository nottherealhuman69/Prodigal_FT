import requests
from datetime import datetime
from typing import List, Dict
from config import HUGGINGFACE_API_TOKEN, MODEL_ID

class NewsletterGenerator:
    def __init__(self):
        self.api_url = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
        self.headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def generate_summary(self, articles: List[Dict]) -> str:
        """Generate a summary of articles using Hugging Face API"""
        try:
            # Create a prompt with article titles
            article_titles = "\n".join([f"- {article['title']}" for article in articles])
            
            prompt = f"""
            Create a brief summary of today's top Web3 and cryptocurrency news based on these headlines:
            
            {article_titles}
            
            Write a concise 2-3 sentence summary highlighting the key trends and important developments.
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').replace(prompt, '').strip()
                else:
                    return "Today's Web3 news covers various developments in cryptocurrency, blockchain technology, and digital assets."
            else:
                print(f"API Error: {response.status_code}")
                return "Today's Web3 news covers various developments in cryptocurrency, blockchain technology, and digital assets."
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Today's Web3 news covers various developments in cryptocurrency, blockchain technology, and digital assets."
    
    def create_newsletter(self, articles: List[Dict]) -> str:
        """Create a complete newsletter"""
        today = datetime.now().strftime("%B %d, %Y")
        
        # Generate AI summary
        ai_summary = self.generate_summary(articles)
        
        # Newsletter header
        newsletter = f"""
🚀 **Daily Web3 Newsletter - {today}**

📊 **Today's Summary:**
{ai_summary}

📰 **Top Stories:**

"""
        
        # Add articles
        for i, article in enumerate(articles, 1):
            newsletter += f"""
**{i}. {article['title']}**
🔗 Source: {article['source']}
📖 {article['description']}
🌐 Link: {article['link']}

"""
        
        # Newsletter footer
        newsletter += """
---
🔔 Stay updated with the latest Web3 news!
📱 Follow us for daily crypto insights.

*This newsletter is automatically generated using AI.*
"""
        
        return newsletter