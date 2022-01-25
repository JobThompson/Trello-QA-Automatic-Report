class TrelloList:
    def __init__(self, list_info, card_data):
        self.name = list_info['name']
        self.id = list_info['id']
        self.board_id = list_info['idBoard']
        self.cards = card_data
        self.card_objects = []