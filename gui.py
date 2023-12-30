import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkhtmlview import HTMLLabel
from user_geo import get_user_geo
from tfidf import calculate_tfidf_for_queries, ranked_retrieval_tfidf
from query_expansion import  expand_query_based_on_synonyms, expand_query_based_on_translation
from preprocess import preprocess_text
from user_history import save_user_history
import requests
from io import BytesIO
import webbrowser



class GameCard(ttk.Frame):
    def __init__(self, master, game_info, image_url, open_steam_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.game_info = game_info
        self.image_url = image_url
        self.open_steam_callback = open_steam_callback

        # Set style for the card
        self.configure(style="GameCard.TFrame")

        # Create widgets for the card
        self.create_widgets()

    def create_widgets(self):
        # Image
        image = self.load_image(self.image_url)
        image_label = ttk.Label(self, image=image, style="GameCard.TLabel")
        image_label.image = image
        image_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky='w')

        # Title
        title_label = ttk.Label(self, text=self.game_info.get('name', 'Unknown Title'), font=('Helvetica', 14, 'bold'), style="GameCard.TLabel")
        title_label.grid(row=0, column=1, columnspan=2, pady=5, sticky='w')

        # Small Description
        desc_label = HTMLLabel(self, html=self.game_info.get('short_description', 'No description available'), wraplength=400, style="GameCard.TLabel")
        desc_label.grid(row=1, column=1, columnspan=2, pady=5, sticky='w')

        # Price
        price_label = ttk.Label(self, text=f"Price: {self.game_info.get('price', 'Free')}", style="GameCard.TLabel")
        price_label.grid(row=2, column=1, pady=5, sticky='w')

        # More Details Button
        details_button = ttk.Button(self, text="More Details", command=self.show_more_details, style="GameCard.TButton")
        details_button.grid(row=3, column=0, columnspan=3, pady=10)

    def load_image(self, url):
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            image.thumbnail((100, 100))  # Adjust size as needed
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image from URL: {e}")
            # Provide a default image if loading fails
            default_image = Image.open('data/image-not-found.png')  # Replace 'default_image.png' with your default image file
            default_image.thumbnail((450, 400))
            return ImageTk.PhotoImage(default_image)

    def show_more_details(self):
        # Implement the functionality to show more details for the selected game
        pass

    def open_steam_store(self):
        if self.open_steam_callback:
            app_id = self.game_info.get('steam_appid')
            if app_id:
                self.open_steam_callback(app_id)



class GameCatalog(tk.Frame):
    def __init__(self, master, results, game_data, image_data, **kwargs):
        super().__init__(master, **kwargs)
        self.results = results
        self.game_data = game_data
        self.image_data = image_data

        # Create a scrollable canvas
        canvas = tk.Canvas(self)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame to hold the game cards
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Create game cards
        for i, result in enumerate(self.results):
            app_id = result[1]
            game_info = self.game_data.loc[self.game_data['steam_appid'] == app_id].iloc[0]
            image_url = self.image_data.loc[self.image_data['steam_appid'] == app_id, 'header_image'].iloc[0]

            game_card = GameCard(frame, game_info, image_url, relief="solid", bd=1)
            game_card.grid(row=i, column=0, padx=10, pady=10, sticky='n')

        # Bind the canvas to the scrollbar
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Make the canvas scrollable with the mouse wheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))


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
        text_bg_color = "#171a21"
        entry_bg_color = "#40444b"
        scrollbar_color = "#001C4D"
        active_bg_color = "#7289da"

        style.configure("TButton", padding=6, relief="flat", background=active_bg_color, foreground=fg_color)
        style.map("TButton", background=[("active", "#677bc4")])
        style.configure("TEntry", padding=6, fieldbackground=entry_bg_color, foreground=fg_color)
        style.configure("TFrame", background=bg_color)
        style.configure("Dark.TLabel", background=text_bg_color, foreground=fg_color)
        style.configure("TScrollbar", troughcolor=scrollbar_color, background=scrollbar_color, bordercolor=bg_color)

        
        style.configure("GameCard.TFrame", background="#000000", borderwidth=4, relief="solid")
        style.configure("GameCard.TLabel", background="#f0f0f0", foreground="black")
        style.configure("GameCard.TButton", padding=6, relief="flat", background="#7289da", foreground="white")
        style.map("GameCard.TButton", background=[("active", "#677bc4")])
        # Entry and Button
        self.query_entry = ttk.Entry(self.master, width=50, style="TEntry")
        self.query_button = ttk.Button(self.master, text="Submit Query", command=self.handle_query, style="TButton")

        # Pack Entry and Button
        self.query_entry.pack(pady=10, padx=10)
        self.query_button.pack(pady=10)

        # Create a canvas with vertical scrollbar
        self.canvas = tk.Canvas(self.master, bg=bg_color, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a frame to hold the content
        self.result_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="nw")

        # Create a vertical scrollbar and associate it with the canvas
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview, style="TScrollbar")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the scrollbar to the right of the canvas
        self.scrollbar.pack(side="right", fill="y")

        # Bind the on_canvas_configure method to the Configure event of the canvas
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Center the content vertically and horizontally
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)

        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.inverted_index = inverted_index
        self.user_history = user_history
        self.main_data = main_data
        self.game_data = game_data
        self.image_data = image_data

    def on_canvas_configure(self, event):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        x = (width - self.result_frame.winfo_reqwidth()) // 2
        y = (height - self.result_frame.winfo_reqheight()) // 2

        self.canvas.create_window(x, y, anchor="nw", window=self.result_frame)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def handle_query(self):
        query_text = self.query_entry.get()
        if query_text:
            user_ip, user_country = get_user_geo()
            print(f"User IP: {user_ip}, User Country: {user_country}")

            expanded_query_synonyms = expand_query_based_on_synonyms(preprocess_text(query_text, True, True))
            expanded_query_translation = expand_query_based_on_translation(expanded_query_synonyms)

            expanded_query = f"{expanded_query_translation}"

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

                # Display additional information from main_data
                additional_info = f"Release Date: {game_name.get('release_date', 'N/A')}\n"
                additional_info += f"Developer: {game_name.get('developer', 'N/A')}\n"
                additional_info += f"Publisher: {game_name.get('publisher', 'N/A')}\n"
                additional_info += f"Genres: {game_name.get('genres', 'N/A')}\n"
                additional_info += f"Steamspy Tags: {game_name.get('steamspy_tags', 'N/A')}\n"
                additional_info += f"Price: {game_name.get('price', 'N/A')} $"

            # Create a frame to hold the card elements
            card_frame = ttk.Frame(self.result_frame, style="TFrame", relief="solid", borderwidth=2)
            card_frame.pack(pady=10, padx=10, fill="both", expand=True, side="top", anchor="n")

            
            # Center the card within the canvas
            card_frame.pack(side="top", anchor="n")

            # Display image on the left side of the card
            if 'steam_appid' in self.image_data.columns and app_id in self.image_data['steam_appid'].values:
                image_url = self.image_data.loc[self.image_data['steam_appid'] == app_id, 'header_image'].iloc[0]
                try:
                    response = requests.get(image_url)
                    image = Image.open(BytesIO(response.content))

                    # Adjust thumbnail size to fit the card
                    thumbnail_size = (500, 350)
                    image.thumbnail(thumbnail_size)

                    photo = ImageTk.PhotoImage(image)
                    image_label = ttk.Label(card_frame, image=photo, style="Dark.TLabel")
                    image_label.image = photo  # Keep a reference to the image to prevent it from being garbage collected
                    image_label.pack(side="left", padx=10)

                except Exception as e:
                    print(f"Error loading image from URL: {e}")

            # Create a frame to hold text on the right side of the card
            text_frame = ttk.Frame(card_frame, style="TFrame")
            text_frame.pack(side="right", fill="both", expand=True)

            # Display description text
            if 'short_description' in game_info:
                game_description = f"Description : {game_info['short_description']}"
                description_label = ttk.Label(text_frame, text=game_description, wraplength=400, style="Dark.TLabel")
                description_label.pack()

            # Add a line space between description and additional information
            ttk.Separator(text_frame, orient="horizontal").pack(fill="x", pady=10)
            
            # Display additional information from main_data
            info_label = ttk.Label(text_frame, text=additional_info, style="Dark.TLabel")
            info_label.pack(padx=0, pady=5, anchor="w")  # Adjust padx as needed

            # Add space between games
            ttk.Separator(self.result_frame, orient="horizontal").pack(fill="x", pady=10)
            
            # Display the "Open Steam Store" button
            open_store_button = ttk.Button(text_frame, text="Open Steam Store", command=lambda app_id=app_id: self.open_steam_store(app_id), style="GameCard.TButton")
            open_store_button.pack(padx=0, pady=5, anchor="w")

        # Update the canvas size based on the content
        self.canvas.update_idletasks()

        # Update the canvas scroll region after changing the content
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def open_steam_store(self, app_id):
        # Implement the functionality to open the Steam Store for the selected game
        steam_store_url = f"https://store.steampowered.com/app/{app_id}/"
        webbrowser.open(steam_store_url)   
