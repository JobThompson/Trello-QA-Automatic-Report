from API import trello_get
from Config_Import import json_config

class TrelloCard:
    def __init__(self, card_info, list_name):
        self.name = card_info['name']
        self.list_name = list_name
        self.id = card_info['id']
        self.url = card_info['url']
        self.labels = card_info['labels']
        self.dev_team_assigned = self.get_dev_team()
        self.passedTestCases = 0
        self.failedTestCases = 0
        self.passedRetestCases = 0
        self.failedRetestCases = 0
        # self.numberOfComments = card_info['badges']['comments']
        # self.members = self.get_members()
        self.testers = self.get_testers()
        self.testCases = []
        self.retestedCases = []
        self.isInOriginList = self.get_origin_list()
        self.status = self.get_status()
        self.get_test_cases()
        self.NumberOfTestCases = self.get_num_of_test_cases()

    def get_num_of_test_cases(self):
        return (self.passedTestCases + self.failedTestCases) + (self.passedRetestCases + self.failedRetestCases)

    # def get_members(self):
    #     request = trello_get(f'cards/{self.id}/members?')
    #     return request.json()
    
    def get_testers(self):
        testers = ''
        for i in self.labels:
            if i['name'] in json_config['TEAM_MEMBERS']:
                testers = testers + i['name'] +', '
        testers = testers[:len(testers) - 2]
        return testers
    
    def get_status(self):
        label_names = []
        for i in self.labels:
            label_names.append(i['name'])
        if 'Failed' in label_names and 'Passed' not in label_names:
            status = 'Failed'
        elif 'Passed' in label_names and 'Failed' not in label_names:
            status = 'Passed'
        elif 'In Development' in label_names:
            status = 'In Development'
        else:
            status = 'Pending'
        return status

    def get_dev_team(self):
        team = 'Unassigned'
        for i in self.labels:
            if 'Team: Kevin Moore' in i['name']:
                team = 'Kevin Moore'
                break
            elif 'Team: Zack Baker' in i['name']:
                team = 'Zack Baker'
                break                
        return team
            

    def get_origin_list(self):
        for i in self.labels:
            if f'Origin: {self.list_name}' in i['name']: 
                return True
        return False
            
    def get_test_cases(self):
        test_cases = []
        retested_cases = []
        request = trello_get(f'cards/{self.id}/actions?')
        actions = request.json()
        for i in actions:
            try:
                stripped_text = i['data']['text'].replace(' ', '')
                stripped_text = stripped_text.lower()
            except:
                stripped_text = ''
            if i['type'] == 'commentCard' and ('passorfail:' in stripped_text):
                if (any(entry in stripped_text for entry in ['type:positive', 'type:negative'])):
                    test_cases.append(i)
                    if any(entry in stripped_text for entry in ['passorfail:pass', 'passorfail:passed', 'passorfail:**passed**', 'passorfail:**pass**', 'passorfail:*passed*', 'passorfail:*pass*', 'passorfail:***passed***', 'passorfail:***pass***']):
                        self.passedTestCases += 1
                    elif any(entry in stripped_text for entry in ['passorfail:fail', 'passorfail:failed', 'passorfail:**failed**', 'passorfail:*fail*', 'passorfail:***fail***', 'passorfail:***fail***']):
                        self.failedTestCases += 1
                elif(any(entry in stripped_text for entry in ['type:r-positive', 'type:r-negative'])):
                    retested_cases.append(i)
                    if 'passorfail:pass' in stripped_text:
                        self.passedRetestCases += 1
                    elif 'passorfail:fail' in stripped_text:
                        self.failedRetestCases += 1
        self.testCases = test_cases
        self.retestedCases = retested_cases