import pandas as pd
import os
from inverted_index import build_inverted_index_tfidf , save_inverted_index
from tfidf import calculate_tfidf_for_queries, ranked_retrieval_tfidf
from preprocess import preprocess_text


# Load the preprocessed data
data = pd.read_csv('data/steam.csv')  # Adjust the file path if needed


# Assuming you have the necessary paths and files
current_dir = os.path.dirname(os.path.abspath(__file__))


# Apply preprocessing to all columns (excluding 'appid' and 'document')
for column in data.columns:
    if column not in ['a//ppid', 'document']:
        data[f'{column}_tokens'] = data[column].apply(lambda x: preprocess_text(x))
        
        
# Save the preprocessed data to a JSON file
data.to_json('preprocessed_data_all_columns.json', orient='records', lines=True)

inverted_index = build_inverted_index_tfidf(data)
# Save the inverted index to a file
save_inverted_index(inverted_index)


# Get user input for queries
queries = []
while True:
    query_number = input("Enter query number (type '0' to stop): ")
    if query_number == '0':
        break
    query_text = input("Enter query text: ")
    queries.append((int(query_number), query_text))

# Calculate TF-IDF for queries
tfidf_queries = calculate_tfidf_for_queries(queries, inverted_index)

# Perform ranked retrieval with TF-IDF
results = ranked_retrieval_tfidf(tfidf_queries, inverted_index)

# Save results to a file
with open('tfidf_results.txt', 'w') as result_file:
    for result in results:
        result_file.write(','.join(map(str, result)) + '\n')
        

results_file = os.path.join(current_dir, 'tfidf_results.txt')  # Update the filename
