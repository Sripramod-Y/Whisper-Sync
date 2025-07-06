import re

def clean_transcript(transcript: str) -> str:
    # Remove filler words
    fillers = ["uh","um","mm","hmm"]
    pattern = re.compile(r'\b(' + '|'.join(fillers) + r')\b', re.IGNORECASE)
    cleaned = pattern.sub(" ", transcript)
    # Fix slutters 
    cleaned = re.sub(r'(\w+)-(\1)', r'\1', cleaned)

    return cleaned.strip()