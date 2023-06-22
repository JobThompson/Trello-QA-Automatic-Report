from TrelloTeamMember import Team_Member
from Config_Import import json_config

class TrelloReport:
    def __init__(self, name, card_objects):
        self.list_name = name #
        self.NumberOfCards = 0 #
        self.NumberOfTestCases = 0 #
        self.NumberOfBugCards = 0 #
        self.NumberOfBlockedCards = 0 #
        self.NumberOfCardsPendingRetest = 0 #
        self.NumberOfRetestedCardsFailed = 0 #
        self.NumberOfRetestedCardsPassed = 0 #
        self.NumberOfFrontEndCards = 0 #
        self.NumberOfBackEndCards = 0 #
        self.NumberOfFailedFrontEndCards = 0 #
        self.NumberOfFailedBackEndCards = 0 #
        self.NumberOfPassedFrontEndCards = 0 #
        self.NumberOfPassedBackEndCards = 0 #
        self.NumberOfCardsNotInOriginSprint = 0 #
        self.CardsByYear = {} #
        self.CardsByMonth = {} #
        self.CardsByMonthAndYear = {} #
        self.TeamMemberStats = self.get_team_members() 
        self.NumberOfRetestedCards = self.get_num_of_retested() #
        self.NumberOfFrontEndCardsPendingTest = self.get_front_end_pending() #
        self.NumberOfBackEndCardsPendingTest = self.get_back_end_pending() #
        self.NumberOfPassedCards = self.get_num_passed() #
        self.NumberOfFailedCards = self.get_num_failed() #
        self.NumberOfTestedCards = self.get_num_tested()  #
        self.NumberOfCardsAwaitingTesting = self.get_num_awaiting_testing()  #
        self.card_objects = card_objects #

    def get_num_of_retested(self):
        return self.NumberOfRetestedCardsPassed + self.NumberOfRetestedCardsFailed

    def get_front_end_pending(self):
        return self.NumberOfFrontEndCards - (self.NumberOfFailedFrontEndCards + self.NumberOfPassedFrontEndCards)

    def get_back_end_pending(self):
        return self.NumberOfBackEndCards - (self.NumberOfFailedBackEndCards + self.NumberOfPassedBackEndCards)

    def get_num_passed(self):
        return self.NumberOfPassedBackEndCards + self.NumberOfPassedFrontEndCards

    def get_num_failed(self):
        return self.NumberOfFailedBackEndCards + self.NumberOfFailedFrontEndCards
        
    def get_num_tested(self):
        return (self.NumberOfPassedBackEndCards + self.NumberOfPassedFrontEndCards) + (self.NumberOfFailedBackEndCards + self.NumberOfFailedFrontEndCards)

    def get_num_awaiting_testing(self):
        return self.NumberOfCards - ((self.NumberOfPassedBackEndCards + self.NumberOfPassedFrontEndCards) + (self.NumberOfFailedBackEndCards + self.NumberOfFailedFrontEndCards))

    def get_team_members(self):
        members = []
        for member in json_config['TEAM_MEMBERS']:
            members.append(Team_Member(member))
        return members