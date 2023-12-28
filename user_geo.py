import requests

def get_user_geo():
    try:
        response = requests.get('https://ipinfo.io')
        ip_data = response.json()
        user_ip = ip_data.get('ip')
        user_country = ip_data.get('country')
        return user_ip, user_country
    except Exception as e:
        print(f"Error getting IP information: {e}")
        return None, None
