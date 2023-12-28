from user_geo import get_user_geo
from tfidf import calculate_tfidf_for_queries, ranked_retrieval_tfidf
from query_expansion import expand_query_based_on_synonyms
from preprocess import preprocess_text
from user_history import save_user_history
import tkinter as tk
from tkinter import Label, Entry, Button, Text, Scrollbar


# Define query_entry as a global variable
query_entry = None

def handle_query(inverted_index, user_history):
    global query_entry

    query_text = query_entry.get()
    if query_text:
        # Get user's IP and country
        user_ip, user_country = get_user_geo()
        print(f"User IP: {user_ip}, User Country: {user_country}")

        # Expand query based on manual synonyms
        expanded_query = expand_query_based_on_synonyms(preprocess_text(query_text, True, True))
       

        # Calculate TF-IDF for the query
        tfidf_queries = calculate_tfidf_for_queries([(1, expanded_query)], inverted_index)
        tfidf_query = tfidf_queries[1]
       

        # Use the expanded query in the retrieval process
        results = ranked_retrieval_tfidf([(1, tfidf_query)], inverted_index)

        # Update user history
        update_user_history(query_text, user_history)

        # Display results in the GUI
        display_results(results, query_text, expanded_query)



# Function to update user history
def update_user_history(query_text, user_history):
    user_id = 1  # For simplicity, consider a single user
    if user_id not in user_history:
        user_history[user_id] = {'queries': []}
    user_history[user_id]['queries'].append(query_text)
    save_user_history(user_history)

def display_results(results, original_query, expanded_query):
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)

    # Display original and expanded queries
    result_text.insert(tk.END, f"Original Query: {original_query}\n")
    result_text.insert(tk.END, f"Expanded Query: {expanded_query}\n\n")

    # Display retrieval results
    for result in results:
        result_text.insert(tk.END, f"Document ID: {result[1]}, Score: {result[2]}\n")

    result_text.config(state=tk.DISABLED)


# Function to create the GUI
def gui(inverted_index,user_history):
    global query_entry  # Access the global variable

    # Create the main window
    root = tk.Tk()
    root.title("Information Retrieval System")

    # Create and place widgets in the window
    Label(root, text="Enter Query:").pack(pady=10)
    query_entry = Entry(root, width=50)
    query_entry.pack(pady=10)
    query_button = Button(root, text="Submit Query", command=lambda: handle_query(inverted_index, user_history))
    query_button.pack(pady=10)

    global result_text  # Define result_text as a global variable
    result_text = Text(root, wrap=tk.WORD, height=10, width=50)
    result_text.pack(pady=10)

    # Add scrollbar to the result text widget
    scrollbar = Scrollbar(root, command=result_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    result_text.config(yscrollcommand=scrollbar.set)

    # Start the GUI main loop
    root.mainloop()

