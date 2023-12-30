import json

# user_history.py

def load_user_history(filename='user_history.json'):
    try:
        with open(filename, 'r') as f:
            user_history = json.load(f)

    except FileNotFoundError:
        user_history = {}
    return user_history




# user_history.py

# user_history.py

def save_user_history(user_history, query_text, app_id, filename='user_history.json'):
    # Ensure that the key exists before accessing its value
    if query_text not in user_history:
        user_history[query_text] = []

    # Add the app_id to the list
    user_history[query_text].append(app_id)

    with open(filename, 'w') as f:
        json.dump(user_history, f, indent=2)

