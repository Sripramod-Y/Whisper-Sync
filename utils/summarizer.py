import re
from typing import List
import nltk
from rake_nltk import Rake

def normalize_transcript(text: str) -> str:
    """Fix punctuation and formatting for processing"""
    # 1. Add missing periods after obvious sentence endings
    text = re.sub(r'(\w)(\n[A-Z])', r'\1. \2', text)  
    text = re.sub(r'(\w)([ ]{2,}[A-Z])', r'\1. \2', text)  
    
    # 2. Standardize speaker notations
    text = re.sub(r'(\n\s*[A-Z][a-z]+:)', r'. \1', text) 
    
    # 3. Clean remaining formatting
    text = text.replace('\n', ' ')
    text = re.sub(r' +', ' ', text)
    return text.strip()

def extract_keyphrases(text: str) -> List[str]:
    """Improved phrase extraction with punctuation handling"""
    # Force sentence boundaries
    text = normalize_transcript(text)
    
    r = Rake()
    r.extract_keywords_from_text(text)
    return [
        phrase.capitalize().strip('.')
        for phrase in r.get_ranked_phrases()[:7]
        if len(phrase.split()) > 1
    ]

def find_action_items(text: str) -> List[str]:
    """Robust action item detection"""
    nltk.download('punkt', quiet=True)
    
    # Pre-process text
    text = normalize_transcript(text)
    sentences = nltk.sent_tokenize(text)
    
    actions = []
    triggers = ["please", "need to", "should", "will", "action", "assign"]
    
    for sent in sentences:
        lower_sent = sent.lower()
        if any(trigger in lower_sent for trigger in triggers):
            # Clean and extract action
            action = re.sub(r'^.*?:', '', sent).strip()  # Remove speaker
            action = re.sub(r'^(.*?\b(?:please|should|need to)\b)', '', action, flags=re.I).strip()
            action = action.split('.')[0].split('!')[0].strip()
            
            if 10 < len(action) < 100:  # Validate length
                actions.append(action.capitalize())
    
    return list(set(actions))[:5]  # Deduplicate

