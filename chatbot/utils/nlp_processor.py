import nltk
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from pathlib import Path

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class NLPProcessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer()
        self.faq_data = self.load_faq_data()
        
    def load_faq_data(self):
        """Load FAQ data from JSON files"""
        base_dir = Path(__file__).parent.parent.parent
        faq_file = base_dir / 'knowledge_base' / 'faqs.json'
        
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default FAQ structure
            return {
                "admissions": [],
                "courses": [],
                "registration": [],
                "facilities": []
            }
    
    def preprocess_text(self, text):
        """Preprocess text by tokenizing, removing stopwords, and stemming"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem
        processed_tokens = [
            self.stemmer.stem(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        return ' '.join(processed_tokens)
    
    def find_best_match(self, query, category=None):
        """Find the best matching FAQ for the given query"""
        query_processed = self.preprocess_text(query)
        
        best_match = None
        best_score = 0
        best_category = None
        
        # Search through all categories or specific category
        categories_to_search = [category] if category else self.faq_data.keys()
        
        for cat in categories_to_search:
            for faq in self.faq_data.get(cat, []):
                question_processed = self.preprocess_text(faq['question'])
                
                # Simple cosine similarity
                vectors = self.vectorizer.fit_transform([query_processed, question_processed])
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                
                # Keyword matching bonus
                keywords = faq.get('keywords', '').split(',')
                keyword_bonus = sum(1 for keyword in keywords if keyword.strip().lower() in query.lower()) * 0.1
                
                total_score = similarity + keyword_bonus
                
                if total_score > best_score:
                    best_score = total_score
                    best_match = faq
                    best_category = cat
        
        return best_match, best_score, best_category
    
    def extract_category(self, query):
        """Extract potential category from query"""
        query_lower = query.lower()
        category_keywords = {
            'admissions': ['admission', 'apply', 'application', 'requirement', 'entry'],
            'courses': ['course', 'program', 'degree', 'subject', 'curriculum'],
            'registration': ['register', 'registration', 'enroll', 'enrollment'],
            'facilities': ['facility', 'library', 'hostel', 'accommodation', 'lab']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
