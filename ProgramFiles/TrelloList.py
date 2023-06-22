class TrelloList:
    def __init__(self, list_info):
        self.name = list_info['name']
        self.id = list_info['id']
        self.board_id = list_info['idBoard']
        self.card_objects = []