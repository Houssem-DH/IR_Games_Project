import json
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

# user_history.py

def load_user_history(filename=resource_path('data/json/user_history.json')):
    try:
        with open(filename, 'r') as f:
            user_history = json.load(f)

    except FileNotFoundError:
        user_history = {}
    return user_history




# user_history.py

# user_history.py

def save_user_history(user_history, query_text, app_id, filename=resource_path('data/json/user_history.json')):
    # Ensure that the key exists before accessing its value
    if query_text not in user_history:
        user_history[query_text] = []

    # Add the app_id to the list
    user_history[query_text].append(app_id)

    with open(filename, 'w') as f:
        json.dump(user_history, f, indent=2)

