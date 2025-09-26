import random
from .nlp_processor import NLPProcessor

class ResponseGenerator:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.greetings = [
            "Hello! How can I help you with Federal University Wukari today?",
            "Hi there! What would you like to know about FU Wukari?",
            "Welcome! I'm here to assist with FU Wukari information.",
            "Greetings! How can I assist you with university-related queries?"
        ]
        
        self.fallback_responses = [
            "I'm not sure I understand. Could you rephrase your question about FU Wukari?",
            "I'm still learning about FU Wukari. Could you try asking differently?",
            "That's an interesting question. Currently, I'm focused on FU Wukari FAQs.",
            "I specialize in FU Wukari information. Could you ask about admissions, courses, or facilities?"
        ]
    
    def generate_response(self, user_message, session_id=None):
        """Generate response for user message"""
        user_message = user_message.strip()
        
        # Check for greetings
        if self.is_greeting(user_message):
            return random.choice(self.greetings), 1.0, "greeting"
        
        # Extract category
        category = self.nlp_processor.extract_category(user_message)
        
        # Find best match
        best_match, confidence, matched_category = self.nlp_processor.find_best_match(user_message, category)
        
        if best_match and confidence > 0.3:
            response = best_match['answer']
            # Add category context if helpful
            if matched_category and matched_category != category:
                response = f"Regarding {matched_category.replace('_', ' ').title()}:\n{response}"
            return response, confidence, matched_category
        else:
            return random.choice(self.fallback_responses), confidence, "unknown"
    
    def is_greeting(self, text):
        """Check if the text is a greeting"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in text.lower() for greeting in greetings)
