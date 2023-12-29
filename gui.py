import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from user_geo import get_user_geo
from tfidf import calculate_tfidf_for_queries, ranked_retrieval_tfidf
from query_expansion import expand_query_based_on_spacy, expand_query_based_on_synonyms, expand_query_based_on_translation
from preprocess import preprocess_text
from user_history import save_user_history
import requests
from io import BytesIO


class InformationRetrievalApp:
    def __init__(self, master, inverted_index, user_history, main_data, game_data, image_data):
        self.master = master
        self.master.title("Information Retrieval System")

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")  # Choose a different theme for a modern look

        # Configure colors
        bg_color = "#171a21"
        fg_color = "white"
        text_bg_color = "#2c2f33"
        entry_bg_color = "#40444b"
        scrollbar_color = "#40444b"
        active_bg_color = "#7289da"

        style.configure("TButton", padding=6, relief="flat", background=active_bg_color, foreground=fg_color)
        style.map("TButton", background=[("active", "#677bc4")])
        style.configure("TEntry", padding=6, fieldbackground=entry_bg_color, foreground=fg_color)
        style.configure("TFrame", background=bg_color)
        style.configure("Dark.TLabel", background=text_bg_color, foreground=fg_color)
        style.configure("TScrollbar", troughcolor=scrollbar_color, background=scrollbar_color, bordercolor=bg_color)

        self.query_entry = ttk.Entry(self.master, width=50, style="TEntry")
        self.query_entry.pack(pady=10)

        self.query_button = ttk.Button(self.master, text="Submit Query", command=self.handle_query, style="TButton")
        self.query_button.pack(pady=10)

        self.canvas = tk.Canvas(self.master, bg=bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.result_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="center")

        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview, style="TScrollbar")
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.inverted_index = inverted_index
        self.user_history = user_history
        self.main_data = main_data
        self.game_data = game_data
        self.image_data = image_data


    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def handle_query(self):
        query_text = self.query_entry.get()
        if query_text:
            user_ip, user_country = get_user_geo()
            print(f"User IP: {user_ip}, User Country: {user_country}")

            expanded_query_spacy = expand_query_based_on_spacy(query_text)
            expanded_query_synonyms = expand_query_based_on_synonyms(preprocess_text(expanded_query_spacy, True, True))
            expanded_query_translation = expand_query_based_on_translation(expanded_query_synonyms)

            expanded_query = f"{expanded_query_spacy} {expanded_query_synonyms} {expanded_query_translation}"

            tfidf_queries = calculate_tfidf_for_queries([(1, expanded_query)], self.inverted_index)
            tfidf_query = tfidf_queries[1]

            results = ranked_retrieval_tfidf([(1, tfidf_query)], self.inverted_index)

            print(f"Query: {query_text}")
            print(f"Expanded Query: {expanded_query}")
            print(f"Results: {results}")

            self.display_game_info(results[:5])  # Display only top 5 results

    def display_game_info(self, results):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        if not results:
            return

        top_results = results[:5]  # Display only the top 5 results

        for result in top_results:
            app_id = result[1]

            if 'steam_appid' in self.game_data.columns:
                game_info = self.game_data.loc[self.game_data['steam_appid'] == app_id].iloc[0]
            else:
                print("Warning: 'steam_appid' column not found in game_data.")
                return

            if 'appid' in self.main_data.columns:
                game_name = self.main_data.loc[self.main_data['appid'] == app_id].iloc[0]
            else:
                game_name = 'Game Name Not Found'

            if 'name' in game_name:
                gamename = game_name['name']
                ttk.Label(self.result_frame, text=f"Game Name: {gamename}", style="Dark.TLabel").pack()

            if 'detailed_description' in game_info:
                game_description = game_info['detailed_description']
                ttk.Label(self.result_frame, text=f"Description: {game_description}", style="Dark.TLabel").pack()

            if 'steam_appid' in self.image_data.columns and app_id in self.image_data['steam_appid'].values:
                image_url = self.image_data.loc[self.image_data['steam_appid'] == app_id, 'header_image'].iloc[0]
                try:
                    response = requests.get(image_url)
                    image = Image.open(BytesIO(response.content))
                    image.thumbnail((500, 500))
                    photo = ImageTk.PhotoImage(image)
                    label = ttk.Label(self.result_frame, image=photo, style="Dark.TLabel")
                    label.image = photo  # Keep a reference to the image to prevent it from being garbage collected
                    label.pack()

                except Exception as e:
                    print(f"Error loading image from URL: {e}")



