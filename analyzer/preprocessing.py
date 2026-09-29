import re

def clean_text(text):
    text = text.lower()  # lowercase
    text = re.sub(r'[^a-zA-Z ]', '', text)  # remove symbols
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces
    return text