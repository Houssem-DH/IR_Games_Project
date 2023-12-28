import pandas as pd
import os
from inverted_index import build_inverted_index_tfidf, save_inverted_index
from preprocess import preprocess_text
from user_history import load_user_history
from gui import gui

# Load the preprocessed data
data = pd.read_csv('data/steam.csv')  # Adjust the file path if needed

# Assuming you have the necessary paths and files
current_dir = os.path.dirname(os.path.abspath(__file__))

# Apply preprocessing to all columns (excluding 'appid' and 'document')
for column in data.columns:
    if column not in ['appid', 'document']:
        data[f'{column}_tokens'] = data[column].apply(lambda x: preprocess_text(x))
        
        


# Save the preprocessed data to a JSON file
data.to_json('preprocessed_data_all_columns.json', orient='records', lines=True)

# Load or initialize user history
user_history = load_user_history()

inverted_index = build_inverted_index_tfidf(data)
# Save the inverted index to a file
save_inverted_index(inverted_index)
gui(inverted_index, user_history)


