# prf.py
from collections import Counter
from tfidf import calculate_tfidf_for_queries, preprocess_text

def pseudo_relevance_feedback(query_results, inverted_index, collection, n_d=1, n_t=5):
    expanded_terms = []

    for query_id, results in query_results.items():
        top_n_results = results[:n_d]

        # Concatenate content of top n_d documents
        concatenated_text = ' '.join([collection[doc_id]['content'] for doc_id, _ in top_n_results])

        # Preprocess the concatenated text
        preprocessed_text = preprocess_text(concatenated_text)

        # Calculate TFIDF for each term in the concatenated text
        tfidf_scores = calculate_tfidf_for_queries([(1, preprocessed_text)], inverted_index)[1]

        # Sort terms by TFIDF score and get the top n_t terms
        sorted_terms = [term for term, _ in sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:n_t]]

        expanded_terms.append((query_id, sorted_terms))

    return expanded_terms
