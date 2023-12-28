import json

def load_user_history(filename='user_history.json'):
    try:
        with open(filename, 'r') as f:
            user_history = json.load(f)
    except FileNotFoundError:
        user_history = {}
    return user_history

def save_user_history(user_history, filename='user_history.json'):
    with open(filename, 'w') as f:
        json.dump(user_history, f, indent=2)
