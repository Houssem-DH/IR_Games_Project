import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

nltk.download('stopwords')



# Tokenization, Stemming, and Stop Words Removal
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

def preprocess_text(text, stop=True, stem=True):
    # Handle missing values
    if pd.isnull(text):
        return []

    # Convert to string to handle non-string data types
    text = str(text)

    # Remove non-alphabetic characters before tokenization
    text = ''.join(c if c.isalpha() or c.isspace() else ' ' for c in text)

    # Tokenization
    tokens = word_tokenize(text.lower())  # Convert to lowercase for consistency
    # Remove stop words
    if stop:
        tokens = [token for token in tokens if token not in stop_words]  
    # Stemming
    if stem:
        tokens = [ps.stem(token) for token in tokens]
    return tokens
