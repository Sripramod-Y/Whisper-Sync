import re

def format_transcript(raw_text: str) -> str:
    """Convert raw transcription into properly formatted meeting minutes"""
    # Step 1: Basic cleaning
    text = raw_text.replace('\n', ' ').strip()
    text = re.sub(r' +', ' ', text)
    
    # Step 2: Identify speaker changes (capitalized words followed by colon)
    text = re.sub(r' ([A-Z][a-z]+:)', r'\n\1', text)
    
    # Step 3: Add paragraph breaks after long segments
    sentences = re.split(r'(?<=[.!?]) +', text)
    formatted = []
    current_para = []
    
    for sentence in sentences:
        current_para.append(sentence)
        # Start new paragraph after 3 sentences or speaker change
        if len(current_para) >= 3 or '\n' in sentence:
            formatted.append(' '.join(current_para))
            current_para = []
    
    if current_para:
        formatted.append(' '.join(current_para))
    
    # Step 4: Final formatting
    formatted_text = '\n\n'.join(formatted)
    
    # Step 5: Ensure proper capitalization and punctuation
    formatted_text = re.sub(r'([^.!?\n])(\n|$)', r'\1.\2', formatted_text)
    formatted_text = re.sub(r'(\n[A-Z][a-z]+:)', r'\1 ', formatted_text)
    
    return formatted_text.strip()