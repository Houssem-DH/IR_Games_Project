from collections import defaultdict
from preprocess import preprocess_text
import math

def calculate_tfidf_for_queries(queries, inverted_index):
    tfidf_queries = []
    for query_number, query_text in queries:
        tokens = preprocess_text(query_text, True, True)
        tfidf_query = defaultdict(lambda: 0)
        for term in tokens:
            if term in inverted_index:
                tf = tokens.count(term) / len(tokens)
                idf = math.log(len(inverted_index) / inverted_index[term]['document_frequency'] + 1)
                tfidf_query[term] = tf * idf
        tfidf_queries.append((query_number, tfidf_query))
    return tfidf_queries

def ranked_retrieval_tfidf(queries, inverted_index):
    results = []
    for query_number, tfidf_query in queries:
        scores = defaultdict(lambda: 0)
        for term, tfidf_query_term in tfidf_query.items():
            if term in inverted_index:
                for doc_id, tfidf_doc_term in inverted_index[term]['tfidf'].items():
                    scores[doc_id] += tfidf_query_term * tfidf_doc_term

        query_norm = math.sqrt(sum(val ** 2 for val in tfidf_query.values()))
        for doc_id in scores:
            doc_norm = math.sqrt(sum((inverted_index[term]['tfidf'].get(doc_id, 0) ** 2 for term in tfidf_query.keys())))
            scores[doc_id] /= (query_norm * doc_norm) if query_norm * doc_norm != 0 else 1

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results.extend([(query_number, doc_id, score) for doc_id, score in sorted_results])

    return results
