import nltk
import re
import json
from collections import Counter
import math
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

class SimpleTFIDF:
    def __init__(self):
        self.documents = []
        self.vocabulary = set()
        self.idf = {}
    
    def add_document(self, doc_id, tokens):
        self.documents.append((doc_id, tokens))
        self.vocabulary.update(tokens)
    
    def calculate_idf(self):
        doc_count = len(self.documents)
        for word in self.vocabulary:
            doc_freq = sum(1 for doc_id, tokens in self.documents if word in tokens)
            self.idf[word] = math.log(doc_count / (1 + doc_freq))
    
    def tfidf_vector(self, tokens):
        tf = Counter(tokens)
        vector = {}
        for word in set(tokens):
            if word in self.idf:
                vector[word] = tf[word] * self.idf[word]
        return vector
    
    def cosine_similarity(self, vec1, vec2):
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in set(vec1) | set(vec2))
        norm1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        norm2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot_product / (norm1 * norm2)

class NLPProcessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.tfidf = SimpleTFIDF()
        self.faq_data = self.load_faq_data()
        self.setup_tfidf()
    
    def load_faq_data(self):
        """Load FAQ data from JSON files"""
        base_dir = Path(__file__).parent.parent.parent
        faq_file = base_dir / 'knowledge_base' / 'faqs.json'
        
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "admissions": [],
                "courses": [],
                "registration": [],
                "facilities": []
            }
    
    def setup_tfidf(self):
        """Setup TF-IDF with all FAQ questions"""
        doc_id = 0
        for category, faqs in self.faq_data.items():
            for faq in faqs:
                tokens = self.preprocess_text(faq['question'])
                self.tfidf.add_document(doc_id, tokens)
                doc_id += 1
        self.tfidf.calculate_idf()
    
    def preprocess_text(self, text):
        """Preprocess text by tokenizing, removing stopwords, and stemming"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = word_tokenize(text)
        processed_tokens = [
            self.stemmer.stem(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        return processed_tokens
    
    def find_best_match(self, query, category=None):
        """Find the best matching FAQ for the given query"""
        query_tokens = self.preprocess_text(query)
        query_vector = self.tfidf.tfidf_vector(query_tokens)
        
        best_match = None
        best_score = 0
        best_category = None
        doc_id = 0
        
        categories_to_search = [category] if category else self.faq_data.keys()
        
        for cat in categories_to_search:
            for faq in self.faq_data.get(cat, []):
                question_tokens = self.preprocess_text(faq['question'])
                question_vector = self.tfidf.tfidf_vector(question_tokens)
                
                similarity = self.tfidf.cosine_similarity(query_vector, question_vector)
                
                # Keyword matching bonus
                keywords = faq.get('keywords', '').split(',')
                keyword_bonus = sum(1 for keyword in keywords if keyword.strip().lower() in query.lower()) * 0.1
                
                total_score = similarity + keyword_bonus
                
                if total_score > best_score:
                    best_score = total_score
                    best_match = faq
                    best_category = cat
                
                doc_id += 1
        
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
