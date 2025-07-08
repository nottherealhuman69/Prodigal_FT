from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict
from config import SIMILARITY_THRESHOLD, MAX_ARTICLES

class NewsDeduplicator:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        try:
            texts = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        if not articles:
            return []
        
        unique_articles = []
        
        for article in articles:
            is_duplicate = False
            current_title = article['title'].lower()
            
            for unique_article in unique_articles:
                existing_title = unique_article['title'].lower()
                
                # Check exact match first
                if current_title == existing_title:
                    is_duplicate = True
                    break
                
                # Check similarity
                similarity = self.calculate_similarity(current_title, existing_title)
                if similarity > SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        print(f"Deduplicated: {len(articles)} -> {len(unique_articles)} articles")
        return unique_articles
    
    def get_top_articles(self, articles: List[Dict]) -> List[Dict]:
        """Get top articles (simple ranking by source priority)"""
        # Simple ranking: prioritize certain sources
        source_priority = {
            'CoinDesk': 5,
            'CoinTelegraph': 4,
            'Decrypt': 3,
            'The Block': 2,
            'Bankless': 1
        }
        
        # Sort by source priority
        sorted_articles = sorted(
            articles, 
            key=lambda x: source_priority.get(x['source'], 0),
            reverse=True
        )
        
        return sorted_articles[:MAX_ARTICLES]