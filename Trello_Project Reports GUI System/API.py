import requests
from decouple import config # pip install python-decouple
from TrelloList import TrelloList
from TrelloCard import TrelloCard

API_TOKEN = config('TOKEN')
API_KEY = config('KEY')
API_AUTH = f'key={API_KEY}&token={API_TOKEN}'

def trello_get(call): # pre-formatted API GET request to the Trello API
    request = requests.request(
        "GET", 
        f'https://api.trello.com/1/{call}{API_AUTH}', 
        headers={"Accept": "application/json"}
    )      
    return request

"""BOARD FUNCTIONS"""
def get_boards(): # Gets all the boards avaliable to the user that owns the API token and API key
    board_ids = []
    request = trello_get(f'members/me/boards?')
    for i in request.json():
        board_ids.append({'Name': i['name'], 'ID' : i['id']})
    return board_ids

def filter_boards(board_ids): # Only returns the board specified in the .env file by BOARD_NAME
    for i in board_ids:
        if i['Name'] == config.boardName:
            return i

def get_all_cards(board_information): # Gets all the cards for a given board # CURRENTLY UNUSED
    board_id = board_information['ID']
    request = trello_get(f'boards/{board_id}/cards?')
    return request.json()

"""LIST FUNCTIONS"""
def get_lists(board_information): # Gets the all of the lists from the passed in board
    board_id = board_information['ID']
    request = trello_get(f'boards/{board_id}/lists?')
    return request.json()

def get_list_selection(lists): # Gets the lists that analysis is needed on from the user, seperated by a comma.
    for i in lists:
        print(i['name'])
    lists_to_parse = input('\nType the lists that you want information from, seperated by a comma:\n').lower()
    list_selection = lists_to_parse.replace(' ', '').split(',')
    print('')
    return list_selection
    
def filter_lists(lists, list_selection): 
    # filters the input from the user to lowercase without spaces, and compares it to the passed in lists from the board, also filtered.
    list_information = []
    for i in lists:
        name = i['name'].lower().replace(' ', '')
        if name in list_selection:
            list_information.append(i)
    return list_information

def get_cards_by_list(list_information): # Gets the cards from the lists that are passed in
    cards_by_list = []
    for i in list_information:
        list_id = i['id']
        request = trello_get(f'lists/{list_id}/cards?')
        cards_by_list.append(TrelloList(i, request.json()))
    return cards_by_list
