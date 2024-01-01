# main.py
import pandas as pd
import os
import tkinter as tk
from preprocess import preprocess_text
from inverted_index import build_inverted_index_tfidf
from user_history import load_user_history 
from gui import InformationRetrievalApp
from user_geo import get_user_geo



user_ip, user_country = get_user_geo()

# Load other data files
main_data = pd.read_csv('data/csv/steam.csv')
desc_data = pd.read_csv('data/csv/steam_description_data.csv')
image_data = pd.read_csv('data/csv/steam_media_data.csv')


pr='data/json/preprocessed_data_all_columns.json'

if os.path.exists(pr):
    # Load preprocessed data from file
    data = pd.read_json('data/json/preprocessed_data_all_columns.json', orient='records', lines=True)
else:
    data = pd.read_csv('data/csv/steam.csv')
    
    for column in data.columns:
        if column not in ['appid', 'document']:
            data[f'{column}_tokens'] = data[column].apply(lambda x: preprocess_text(x))

    data.to_json('data/json/preprocessed_data_all_columns.json', orient='records', lines=True)
    
    


# Load user history
user_history = load_user_history()


# Build Inverted Index
inverted_index = build_inverted_index_tfidf(data)



# Create and run the application
app = InformationRetrievalApp(tk.Tk(), inverted_index, user_history, main_data, desc_data, image_data,user_country)
app.master.geometry("1024x768")
app.master.mainloop()
