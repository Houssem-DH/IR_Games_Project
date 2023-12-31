from collections import defaultdict
import math
from preprocess import preprocess_text
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import os
import sys

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def calculate_tfidf_for_queries(queries, inverted_index):
    tfidf_queries = {}
    for query_number, query_text in queries:
        tokens = preprocess_text(query_text, True, True)
        tfidf_query = defaultdict(lambda: 0)
        
        for term in tokens:
            if term in inverted_index:
                tf = tokens.count(term) / len(tokens)
                idf = math.log(len(inverted_index) / inverted_index[term]['document_frequency'] + 1)
                tfidf_query[term] = tf * idf
                
        tfidf_queries[query_number] = tfidf_query
    return tfidf_queries

def ranked_retrieval_tfidf(queries, inverted_index, filter_age):
    if filter_age:
        with open(resource_path('data/txt/appids_with_age_18.txt'), 'r') as file:
            appids_with_age_18 = {int(line.strip()) for line in file}
    else:
        appids_with_age_18 = set()

    results = []

    for query_number, tfidf_query in queries:
        query_vector = np.array([tfidf_query[term] for term in tfidf_query.keys()])
        scores = defaultdict(lambda: 0)

        if query_vector.shape[0] == 0:
            print("Empty query vector. Cannot calculate cosine similarity.")
            return []

        for term, tfidf_query_term in tfidf_query.items():
            if term in inverted_index:
                for doc_id, tfidf_doc_term in inverted_index[term]['tfidf'].items():
                    doc_vector = np.array(
                        [inverted_index[term]['tfidf'].get(doc_id, 0) * (position + 1) for position, term in
                        enumerate(tfidf_query.keys())])

                    if doc_vector.shape[0] == 0:
                        print("Empty document vector. Skipping document:", doc_id)
                        continue

                    scores[doc_id] += tfidf_query_term * tfidf_doc_term

        scores = dict(scores)
        doc_vectors = np.array(
            [[inverted_index[term]['tfidf'].get(doc_id, 0) * (position + 1) for position, term in
            enumerate(tfidf_query.keys())] for doc_id in scores.keys()])

        if doc_vectors.shape[0] == 0:
            print("Empty document vectors. No documents to compare.")
            return []

        cosine_similarities = cosine_similarity([query_vector], doc_vectors)[0]

        sorted_results = sorted(zip(scores.keys(), cosine_similarities), key=lambda x: x[1], reverse=True)

        if filter_age:
            # Filter out games with age 18
            filtered_results = [(query_number, doc_id, score) for doc_id, score in sorted_results if doc_id not in appids_with_age_18]
            results.extend(filtered_results)
        else:
            results.extend([(query_number, doc_id, score) for doc_id, score in sorted_results])

    return results
