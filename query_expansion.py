import json

def expand_query_based_on_country(tfidf_query, user_country):
    # Implement your logic to determine expanded query terms based on the user's country
    # This could involve looking up a predefined set of terms for each country or using a machine learning model
    expanded_query_terms = {'grand': 0.5, 'theft': 0.3}

    # Update the original query with the expanded terms
    for term, weight in expanded_query_terms.items():
        tfidf_query[term] = weight

    return tfidf_query


def expand_query_based_on_synonyms(tfidf_query, synonyms_file='synonyms.json'):
    try:
        with open(synonyms_file, 'r') as f:
            synonyms_data = json.load(f)
            synonyms = synonyms_data.get('synonyms', {})
    except FileNotFoundError:
        print("Synonyms file not found.")
        return tfidf_query

    expanded_query_terms = {}
    for term in tfidf_query.keys():
        expanded_query_terms[term] = tfidf_query[term]

        if term in synonyms:
            for synonym in synonyms[term]:
                expanded_query_terms[synonym] = tfidf_query[term]

    return expanded_query_terms



