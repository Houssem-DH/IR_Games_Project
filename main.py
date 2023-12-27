import pandas as pd
import os
import json
import tkinter as tk
from tkinter import Label, Entry, Button, Text, Scrollbar
from inverted_index import build_inverted_index_tfidf, save_inverted_index
from tfidf import calculate_tfidf_for_queries, ranked_retrieval_tfidf
from preprocess import preprocess_text

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

inverted_index = build_inverted_index_tfidf(data)
# Save the inverted index to a file
save_inverted_index(inverted_index)

# Function to handle query submission
def handle_query():
    query_text = query_entry.get()
    if query_text:
        # Calculate TF-IDF for the query
        tfidf_query = calculate_tfidf_for_queries([(1, query_text)], inverted_index)[0]

        # Perform ranked retrieval with TF-IDF
        results = ranked_retrieval_tfidf([tfidf_query], inverted_index)

        # Display results in the GUI
        display_results(results)

# Function to display results in the GUI
def display_results(results):
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    for result in results:
        result_text.insert(tk.END, f"Document ID: {result[1]}, Score: {result[2]}\n")
    result_text.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("Information Retrieval System")

# Create and place widgets in the window
Label(root, text="Enter Query:").pack(pady=10)
query_entry = Entry(root, width=50)
query_entry.pack(pady=10)
query_button = Button(root, text="Submit Query", command=handle_query)
query_button.pack(pady=10)

result_text = Text(root, wrap=tk.WORD, height=10, width=50)
result_text.pack(pady=10)

# Add scrollbar to the result text widget
scrollbar = Scrollbar(root, command=result_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)

# Start the GUI main loop
root.mainloop()
