import requests
from decouple import config as cf # pip install python-decouple

API_TOKEN = cf('TOKEN')
API_KEY = cf('KEY')
API_AUTH = f'key={API_KEY}&token={API_TOKEN}'

def trello_get(call): # pre-formatted API GET request to the Trello API
    request = requests.request(
        "GET", 
        f'https://api.trello.com/1/{call}{API_AUTH}', 
        headers={"Accept": "application/json"}
    )      
    return request
