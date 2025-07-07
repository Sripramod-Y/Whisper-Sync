from rake_nltk import Rake

def extract_keyphrases(text: str, top_n: int = 5) -> list:
    """ Extract top key phrases using RAKE """
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()[:top_n]

def find_action_items(text : str)-> list : 
    """ Identify action items """
    action_phrases = []
    for sentence in text.split("."):
        if any(verb in sentence.lower() for verb in ["should","need to","must"]):
            action_phrases.append(sentence.strip())

    return action_phrases