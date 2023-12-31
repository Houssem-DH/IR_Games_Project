import json
from nltk.corpus import wordnet
from preprocess import preprocess_text
import spacy
from googletrans import Translator
import langid



# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def expand_query_based_on_spacy(query_tokens):
    expanded_terms = set(query_tokens)
    for token in query_tokens:
        similar_words = [word.text for word in nlp.vocab if word.has_vector and nlp(token).similarity(nlp(word.text)) > 0.5]
        expanded_terms.update(similar_words)

    return expanded_terms



def expand_query_based_on_country(tfidf_query, user_country):
    # Implement your logic to determine expanded query terms based on the user's country
    # This could involve looking up a predefined set of terms for each country or using a machine learning model
    expanded_query_terms = {'grand': 0.5, 'theft': 0.3}

    # Update the original query with the expanded terms
    for term, weight in expanded_query_terms.items():
        tfidf_query[term] = weight

    return tfidf_query


def expand_query_based_on_synonyms(query_tokens, synonyms_file='synonyms.json', max_synonyms=1):
    try:
        with open(synonyms_file, 'r') as f:
            synonyms_data = json.load(f)
            synonyms = synonyms_data.get('synonyms', {})
    except FileNotFoundError:
        print("Synonyms file not found.")
        return ' '.join(query_tokens)

    expanded_query_terms = set(query_tokens)
    check = True

    # Manual synonyms from the provided file
    for term in query_tokens:
        if term in synonyms:
            expanded_query_terms.update(synonyms[term])
            check = False

    # NLTK WordNet synonyms
    for term in query_tokens:
        synonyms_wordnet = get_wordnet_synonyms(term, max_synonyms)
        expanded_query_terms.update(synonyms_wordnet)

    if check:
        # Convert the set to a list for consistent order
        expanded_query_terms_list = list(expanded_query_terms)
        expanded_query = expand_query_based_on_spacy(expanded_query_terms_list)
        return ' '.join(expanded_query)

    return ' '.join(expanded_query_terms)


def get_wordnet_synonyms(term, max_synonyms=1):
    synonyms_wordnet = []
    count = 0
    for synset in wordnet.synsets(term):
        for lemma in synset.lemmas():
            synonym = lemma.name().lower()
            if synonym != term and synonym not in synonyms_wordnet:
                synonyms_wordnet.append(synonym)
                count += 1
                if count >= max_synonyms:
                    break
        if count >= max_synonyms:
            break
    return synonyms_wordnet


def is_english(text):
    # Use langid to detect the language of the text
    lang, _ = langid.classify(text)
    return lang == 'en'

def expand_query_based_on_translation(query_text, target_language='en'):
    if not is_english(query_text):
        translator = Translator()
        translation = translator.translate(query_text, dest=target_language)
        expanded_query_translation = translation.text
        return expanded_query_translation
    else:
        # If the query is already in English, return the original query
        return query_text
    
    
def remove_repetitions(sentence):
    # Tokenize the sentence into words
    words = sentence.split()

    # Create a set of unique words to remove repetitions
    unique_words = set()

    # Reconstruct the sentence with only one occurrence of each unique word
    unique_sentence = []
    for word in words:
        # Convert the word to lowercase for case-insensitive comparison
        lower_word = word.lower()
        
        if lower_word not in unique_words:
            unique_sentence.append(word)
            unique_words.add(lower_word)

    return ' '.join(unique_sentence)
