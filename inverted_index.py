import json
from collections import defaultdict
import math


def build_inverted_index_tfidf(data):
    inverted_index = defaultdict(lambda: {'document_frequency': 0, 'postings': {}, 'tfidf': {}})

    for index, row in data.iterrows():
        doc_id = row['appid']
        tokens_columns = [column for column in data.columns if column.endswith('_tokens')]
        tokens = [token for column in tokens_columns for token in row[column]]

        for position, term in enumerate(tokens):
            inverted_index[term]['document_frequency'] += 1

            if doc_id not in inverted_index[term]['postings']:
                inverted_index[term]['postings'][doc_id] = [position]
            else:
                inverted_index[term]['postings'][doc_id].append(position)

    total_documents = len(data)
    for term, data in inverted_index.items():
        for doc_id, positions in data['postings'].items():
            tf = len(positions) / len(data)
            idf = math.log(total_documents / data['document_frequency'] + 1)
            tfidf = tf * idf
            inverted_index[term]['tfidf'][doc_id] = tfidf

    return inverted_index

def save_inverted_index(inverted_index, filename='inverted_index.json'):
    # Save the inverted index to a file
    with open(filename, 'w') as f:
        json.dump(inverted_index, f, indent=2)
