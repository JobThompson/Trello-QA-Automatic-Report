class Team_Member:
    def __init__(self, member_name):
        self.name = member_name
        self.NumberOfCardsTested = 0
        self.NumberOfCardsPassed = 0
        self.NumberOfCardsFailed = 0
        self.NumberOfCardsRetested = 0
        self.NumberOfBlockedCards = 0
        self.NumberOfCardsPending = 0
