# main.py
import pandas as pd
import os
import tkinter as tk
from inverted_index import build_inverted_index_tfidf, save_inverted_index
from preprocess import preprocess_text
from user_history import load_user_history 
from gui import InformationRetrievalApp


data = pd.read_csv('data/steam.csv')
main_data = pd.read_csv('data/steam.csv')
desc_data = pd.read_csv('data/steam_description_data.csv')
image_data = pd.read_csv('data/steam_media_data.csv')

current_dir = os.path.dirname(os.path.abspath(__file__))

for column in data.columns:
    if column not in ['appid', 'document']:
        data[f'{column}_tokens'] = data[column].apply(lambda x: preprocess_text(x))

data.to_json('preprocessed_data_all_columns.json', orient='records', lines=True)

user_history = load_user_history()

print(user_history)

inverted_index = build_inverted_index_tfidf(data)
save_inverted_index(inverted_index)


app = InformationRetrievalApp(tk.Tk(), inverted_index, user_history, main_data, desc_data, image_data)
app.master.geometry("1024x768")
app.master.mainloop()