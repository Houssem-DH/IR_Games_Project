import json
import nltk
from nltk.corpus import wordnet
from preprocess import preprocess_text

nltk.download('wordnet')

def expand_query_based_on_country(tfidf_query, user_country):
    # Implement your logic to determine expanded query terms based on the user's country
    # This could involve looking up a predefined set of terms for each country or using a machine learning model
    expanded_query_terms = {'grand': 0.5, 'theft': 0.3}

    # Update the original query with the expanded terms
    for term, weight in expanded_query_terms.items():
        tfidf_query[term] = weight

    return tfidf_query


def expand_query_based_on_synonyms(query_tokens, synonyms_file='synonyms.json', max_synonyms=2):
    try:
        with open(synonyms_file, 'r') as f:
            synonyms_data = json.load(f)
            synonyms = synonyms_data.get('synonyms', {})
    except FileNotFoundError:
        print("Synonyms file not found.")
        return ' '.join(query_tokens)

    expanded_query_terms = list(' '.join(preprocess_text(token)) for token in query_tokens)  # Preprocess original query terms

    

    # Manual synonyms from the provided file
    for term in query_tokens:
        if term in synonyms:
            expanded_query_terms.extend(' '.join(preprocess_text(token)) for token in synonyms[term])  # Preprocess manual synonyms

    # NLTK WordNet synonyms
    for term in query_tokens:
        synonyms_wordnet = get_wordnet_synonyms(term, max_synonyms)
        expanded_query_terms.extend(' '.join(preprocess_text(token)) for token in synonyms_wordnet)  # Preprocess synonyms
        
        
    return ' '.join(expanded_query_terms)

def get_wordnet_synonyms(term, max_synonyms=2):
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