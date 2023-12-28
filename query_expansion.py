import json

def expand_query_based_on_country(tfidf_query, user_country):
    # Implement your logic to determine expanded query terms based on the user's country
    # This could involve looking up a predefined set of terms for each country or using a machine learning model
    expanded_query_terms = {'grand': 0.5, 'theft': 0.3}

    # Update the original query with the expanded terms
    for term, weight in expanded_query_terms.items():
        tfidf_query[term] = weight

    return tfidf_query


def expand_query_based_on_synonyms(query_tokens, synonyms_file='synonyms.json'):
    try:
        with open(synonyms_file, 'r') as f:
            synonyms_data = json.load(f)
            synonyms = synonyms_data.get('synonyms', {})
    except FileNotFoundError:
        print("Synonyms file not found.")
        return ' '.join(query_tokens)

    expanded_query_terms = set(query_tokens)
    for term in query_tokens:
        if term in synonyms:
            expanded_query_terms.update(synonyms[term])

    return ' '.join(expanded_query_terms)


