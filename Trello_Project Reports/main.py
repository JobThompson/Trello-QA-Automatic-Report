import requests
from datetime import date
from decouple import config # pip install python-decouple
from pandas import DataFrame, read_excel, ExcelWriter
import fnmatch

"""CONFIG"""
API_TOKEN = config('TOKEN')
API_KEY = config('KEY')
API_AUTH = f'key={API_KEY}&token={API_TOKEN}'
BOARD_NAME = config('BOARD_NAME')
# FILEPATH = "X:/Division - Software Development/QA Team/Job's Files/QA Reports/"
FILEPATH = config('FILEPATH')
AGG_FILE_NAME = config('AGG_FILE_NAME')
SINGLE_FILE_FOLDER = config('SINGLE_FILE_FOLDER/')
TODAY = date.today() 

TEAM_MEMBERS = [
    'Job',
    'Sean',
    'Matthew',
    'Anjana'
]

MONTHS =  [
        'January',
        'Feburary',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December']

single_file_columns = [
                'Sprint Name',
                'Card Total',
                'Test Case Cards',
                'Bug Cards',
                'Total Cards Tested',
                'Total Passed Cards',
                'Total Failed Cards',
                'Total Blocked Cards',
                'Total Front End Cards',
                'Passed Front End Cards',
                'Failed Front End Cards',
                'Total Back End Cards',
                'Passed Back End Cards', 
                'Failed Back End Cards', 
                'Total Retested Cards',
                'Passed Retested Cards',
                'Failed Retested Cards',
                'Number Of Cards Awaiting Initial Test',
                'Front End Cards Awaiting Testing',
                'Back End Cards Awaiting Testing',
                'Number Of Cards Awaiting Retesting',
                'Transient Cards'
            ]

team_member_columns = [
                        'Sprint',
                        'Name',
                        'Total Cards Tested',
                        'Cards Passed',
                        'Cards Failed',
                        'Cards Retested',
                        'Cards Pending',
                        'Blocked Cards'
                    ]

agg_columns = [
                'Date',
                'Sprint Name',
                'Card Total',
                'Test Case Cards',
                'Bug Cards',
                'Total Cards Tested',
                'Total Passed Cards',
                'Total Failed Cards',
                'Total Blocked Cards',
                'Total Front End Cards',
                'Passed Front End Cards',
                'Failed Front End Cards',
                'Total Back End Cards',
                'Passed Back End Cards', 
                'Failed Back End Cards', 
                'Total Retested Cards',
                'Passed Retested Cards',
                'Failed Retested Cards',
                'Number Of Cards Awaiting Initial Test',
                'Front End Cards Awaiting Testing',
                'Back End Cards Awaiting Testing',
                'Number Of Cards Awaiting Retesting',
                'Transient Cards'
            ]

card_report_columns = [
                        'Sprint',
                        'Card Name',
                        'Card Status',
                        'From This Sprint',
                        'Total Test Cases',
                        'Passed Test Cases',
                        'Failed Test Cases',
                        'Passed Retest Cases',
                        'Failed Retest Cases',
                        'Testers',
                        'URL'
                    ]

"""CLASS DEFINITIONS"""
class list_object:
    def __init__(self, list_info, card_data):
        self.name = list_info['name']
        self.id = list_info['id']
        self.board_id = list_info['idBoard']
        self.cards = card_data
        self.card_objects = []

class card_object:
    def __init__(self, card_info, list_name):
        self.name = card_info['name']
        self.list_name = list_name
        self.id = card_info['id']
        self.url = card_info['url']
        self.labels = card_info['labels']
        self.passedTestCases = 0
        self.failedTestCases = 0
        self.passedRetestCases = 0
        self.failedRetestCases = 0
        self.numberOfComments = card_info['badges']['comments']
        self.members = self.getMembers()
        self.testers = self.getTesters()
        self.testCases = []
        self.retestedCases = []
        self.isInOriginList = self.getOriginList()
        self.status = self.getStatus()
        self.getTestCases()
        self.NumberOfTestCases = self.getNumOfTestCases()

    def getNumOfTestCases(self):
        return (self.passedTestCases + self.failedTestCases) + (self.passedRetestCases + self.failedRetestCases)

    def getMembers(self):
        request = trello_get(f'cards/{self.id}/members?')
        return request.json()
    
    def getTesters(self):
        testers = ''
        for i in self.labels:
            if i['name'] in TEAM_MEMBERS:
                testers = testers + i['name'] +', '
        testers = testers[:len(testers) - 2]
        return testers
    
    def getStatus(self):
        label_names = []
        for i in self.labels:
            label_names.append(i['name'])
        if 'Failed' in label_names and 'Passed' not in label_names:
            status = 'Failed'
        elif 'Passed' in label_names and 'Failed' not in label_names:
            status = 'Passed'
        else:
            status = 'Pending'
        return status


    def getOriginList(self):
        for i in self.labels:
            if f'Origin: {self.list_name}' in i['name']: 
                return True
        return False
            
    def getTestCases(self):
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
                    if 'passorfail:pass' in stripped_text:
                        self.passedTestCases += 1
                    elif 'passorfail:fail' in stripped_text:
                        self.failedTestCases += 1
                elif(any(entry in stripped_text for entry in ['type:r-positive', 'type:r-negative'])):
                    retested_cases.append(i)
                    if 'passorfail:pass' in stripped_text:
                        self.passedRetestCases += 1
                    elif 'passorfail:fail' in stripped_text:
                        self.failedRetestCases += 1
        self.testCases = test_cases
        self.retestedCases = retested_cases

class team_member:
    def __init__(self, member_name):
        self.name = member_name
        self.NumberOfCardsTested = 0
        self.NumberOfCardsPassed = 0
        self.NumberOfCardsFailed = 0
        self.NumberOfCardsRetested = 0
        self.NumberOfBlockedCards = 0
        self.NumberOfCardsPending = 0

class report_object:
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
        self.TeamMemberStats = self.getTeamMembers() 
        self.NumberOfRetestedCards = self.getNumOfRetested() #
        self.NumberOfFrontEndCardsPendingTest = self.getFrontEndPending() #
        self.NumberOfBackEndCardsPendingTest = self.getBackEndPending() #
        self.NumberOfPassedCards = self.getNumPassed() #
        self.NumberOfFailedCards = self.getNumFailed() #
        self.NumberOfTestedCards = self.getNumTested()  #
        self.NumberOfCardsAwaitingTesting = self.getNumAwaitingTesting()  #
        self.card_objects = card_objects

    def getNumOfRetested(self):
        return self.NumberOfRetestedCardsPassed + self.NumberOfRetestedCardsFailed

    def getFrontEndPending(self):
        return self.NumberOfFrontEndCards - (self.NumberOfFailedFrontEndCards + self.NumberOfPassedFrontEndCards)

    def getBackEndPending(self):
        return self.NumberOfBackEndCards - (self.NumberOfFailedBackEndCards + self.NumberOfPassedBackEndCards)

    def getNumPassed(self):
        return self.NumberOfPassedBackEndCards + self.NumberOfPassedFrontEndCards

    def getNumFailed(self):
        return self.NumberOfFailedBackEndCards + self.NumberOfFailedFrontEndCards
        
    def getNumTested(self):
        return (self.NumberOfPassedBackEndCards + self.NumberOfPassedFrontEndCards) + (self.NumberOfFailedBackEndCards + self.NumberOfFailedFrontEndCards)

    def getNumAwaitingTesting(self):
        return self.NumberOfCards - ((self.NumberOfPassedBackEndCards + self.NumberOfPassedFrontEndCards) + (self.NumberOfFailedBackEndCards + self.NumberOfFailedFrontEndCards))

    def getTeamMembers(self):
        members = []
        for member in TEAM_MEMBERS:
            members.append(team_member(member))
        return members


"""API FUNCTIONS"""
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
        if i['Name'] == BOARD_NAME:
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
        cards_by_list.append(list_object(i, request.json()))
    return cards_by_list


"""CARD FUNCTIONS"""
def build_cards(cards_by_list): # Creates a card_object for each of the cards in the dictionary passed in, and assigns it to the list_objects card_objects value.
    for i in cards_by_list:
        cards = []
        for e in i.cards:
            cards.append(card_object(e, i.name))
        i.card_objects = cards
    return

"""DATA ANALYSIS FUNCTIONS"""
def anaylze_cards(cards_by_list):
    reports = []
    for i in cards_by_list:
        report = report_object(i.name, i.card_objects)
        for e in i.card_objects:
            labels = []
            report.NumberOfCards += 1
            for u in e.labels:
                labels.append(u['name'])    
            report = get_passed_and_failed_stats(i, report, labels)
        reports.append(report)
    return reports

def get_passed_and_failed_stats(list, report, labels): # Gets the stats from the cards based on the labels that the cards have attached.
    if 'Front End' in labels:
        report.NumberOfFrontEndCards += 1
    elif 'Back End' in labels:
        report.NumberOfBackEndCards += 1

    if 'Test Case' in labels:
        report.NumberOfTestCases += 1
    elif 'Bug' in labels:
        report.NumberOfBugCards += 1

    if 'Blocked' in labels and any(entry in labels for entry in ['Retested', 'Failed', 'Passed']):
        report.NumberOfCardsBlocked += 1

    if 'Failed' in labels and 'Passed' not in labels:
        if 'Front End' in labels:
            report.NumberOfFailedFrontEndCards += 1
        elif 'Back End' in labels:
            report.NumberOfFailedBackEndCards += 1
        if 'Retested' in labels:
            report.NumberOfRetestedCardsFailed += 1
    
    elif 'Passed' in labels and 'Failed' not in labels:
        if 'Front End' in labels:
            report.NumberOfPassedFrontEndCards += 1
        elif 'Back End' in labels:
            report.NumberOfPassedBackEndCards += 1
        if 'Retested' in labels:
            report.NumberOfRetestedCardsPassed += 1

    if 'Retested' in labels and any(entry in labels for entry in ['Passed','Failed']):
        report.NumberOfCardsPendingRetest += 1

    if f'Origin: {list.name}' not in labels:
        report.NumberOfCardsNotInOriginSprint += 1
    
    month = [item for item in labels if item in MONTHS]
    if month[0] in report.CardsByMonth:
        report.CardsByMonth[f'{month[0]}'] += 1
    else:
        report.CardsByMonth[f'{month[0]}'] = 1

    year = fnmatch.filter(labels, '20*')
    if year[0] in report.CardsByYear:
        report.CardsByYear[f'{year[0]}'] += 1
    else:
        report.CardsByYear[f'{year[0]}'] = 1

    if f'{month[0]} - {year[0]}' in report.CardsByMonthAndYear:
        report.CardsByMonthAndYear[f'{month[0]} - {year[0]}'] +=1
    else:
        report.CardsByMonthAndYear[f'{month[0]} - {year[0]}'] = 1

    for i in report.TeamMemberStats:
        if i.name in labels:
            i.NumberOfCardsTested += 1
            if 'Failed' in labels:
                i.NumberOfCardsFailed += 1
            elif 'Passed' in labels:
                i.NumberOfCardsPassed += 1
            else:
                i.NumberOfCardsPending += 1
            if 'Retested' in labels:
                i.NumberOfCardsRetested += 1
            if 'Blocked' in labels and any(entry in labels for entry in ['Retested', 'Failed', 'Passed']): 
                i.NumberOfCardsBlocked += 1
    return report


def get_agg_data():
    try:
        data = read_excel((FILEPATH + AGG_FILE_NAME), sheet_name='Main')
    except Exception as e:
        print('No historical file found, creating new file.')
        data = DataFrame([], columns=agg_columns)
    return data

def build_agg_report(reports):
    agreggate_dataframe = get_agg_data()
    with ExcelWriter(f'{FILEPATH + AGG_FILE_NAME}') as writer:
        for i in reports:
            temp_agreggate_dataframe = DataFrame([[
                f'{TODAY}',
                i.list_name,
                i.NumberOfCards,
                i.NumberOfTestCases,
                i.NumberOfBugCards,
                i.getNumTested(),
                i.getNumPassed(),
                i.getNumFailed(),
                i.NumberOfBlockedCards,
                i.NumberOfFrontEndCards,
                i.NumberOfPassedFrontEndCards,
                i.NumberOfFailedFrontEndCards,
                i.NumberOfBackEndCards,
                i.NumberOfPassedBackEndCards,
                i.NumberOfFailedBackEndCards,
                i.getNumOfRetested(),
                i.NumberOfRetestedCardsPassed,
                i.NumberOfRetestedCardsFailed,
                i.getNumAwaitingTesting(),
                i.getFrontEndPending(),
                i.getBackEndPending(),
                i.NumberOfCardsPendingRetest,
                i.NumberOfCardsNotInOriginSprint
            ]], columns=agg_columns)

            agreggate_dataframe = agreggate_dataframe.append(temp_agreggate_dataframe, ignore_index=True)
        agreggate_dataframe.to_excel(writer, sheet_name='Main', index=False)



def build_single_report(reports):
    with ExcelWriter(f'{FILEPATH}{SINGLE_FILE_FOLDER}{TODAY}- Single Run Report.xlsx') as writer:
        """Main Data"""
        single_run_dataframe = DataFrame([], columns=single_file_columns)
        for i in reports:   
            temp_single_run_dataframe = DataFrame([[
                i.list_name,
                i.NumberOfCards,
                i.NumberOfTestCases,
                i.NumberOfBugCards,
                i.getNumTested(),
                i.getNumPassed(),
                i.getNumFailed(),
                i.NumberOfBlockedCards,
                i.NumberOfFrontEndCards,
                i.NumberOfPassedFrontEndCards,
                i.NumberOfFailedFrontEndCards,
                i.NumberOfBackEndCards,
                i.NumberOfPassedBackEndCards,
                i.NumberOfFailedBackEndCards,
                i.getNumOfRetested(),
                i.NumberOfRetestedCardsPassed,
                i.NumberOfRetestedCardsFailed,
                i.getNumAwaitingTesting(),
                i.getFrontEndPending(),
                i.getBackEndPending(),
                i.NumberOfCardsPendingRetest,
                i.NumberOfCardsNotInOriginSprint
            ]], columns=single_file_columns)

            single_run_dataframe = single_run_dataframe.append(temp_single_run_dataframe, ignore_index=True)
        single_run_dataframe.to_excel(writer, sheet_name='Main', index=False)

        """Team Member Data"""
        team_member_dataframe = DataFrame([], columns=team_member_columns)
        for e in reports:
            for i in e.TeamMemberStats:  
                temp_team_member_dataframe = DataFrame([[
                    e.list_name,
                    i.name,
                    i.NumberOfCardsTested,
                    i.NumberOfCardsPassed,
                    i.NumberOfCardsFailed,
                    i.NumberOfCardsRetested,
                    i.NumberOfCardsPending,
                    i.NumberOfBlockedCards
                ]], columns=team_member_columns)
                team_member_dataframe = team_member_dataframe.append(temp_team_member_dataframe, ignore_index=True)
        team_member_dataframe.to_excel(writer, sheet_name='Team Members', index=False)
    
        """Card Data"""
        card_dataframe = DataFrame([], columns=card_report_columns)
        for e in reports:
            for i in e.card_objects:  
                temp_card_dataframe = DataFrame([[
                    i.list_name,
                    i.name,
                    i.status,
                    i.isInOriginList,
                    i.getNumOfTestCases(),
                    i.passedTestCases,
                    i.failedTestCases,
                    i.passedRetestCases,
                    i.failedRetestCases,
                    i.testers,
                    i.url
                ]], columns=card_report_columns)
                card_dataframe = card_dataframe.append(temp_card_dataframe, ignore_index=True)
        card_dataframe.to_excel(writer, sheet_name='Card Breakdown', index=False)


def get_report_selection():
    while True:
        for i in ['1.Aggregate Only', '2.Single File Only', '3.Aggregate And Single File']:
            print(i)
        response = input('\nSelect the Reports you would like to run: (1-3)\n')
        report_selection = int(response)
        if report_selection not in [1,2,3]:
            print('Selection Not Valid, Please selected a valid menu option.')
        else:
            break
        print('')
    return report_selection


def build_reports(report_selection, reports):
    if report_selection == 1:
        build_agg_report(reports)
    elif report_selection == 2:
        build_single_report(reports)
    elif report_selection == 3:
        build_agg_report(reports)
        build_single_report(reports)

    
"""MAIN"""
def main():
    board_ids = get_boards()
    board_information = filter_boards(board_ids)
    lists = get_lists(board_information)
    report_selection = get_report_selection()
    list_selection = get_list_selection(lists)
    list_information = filter_lists(lists, list_selection)
    cards_by_list = get_cards_by_list(list_information)
    build_cards(cards_by_list)
    reports = anaylze_cards(cards_by_list)
    build_reports(report_selection, reports)
    print('\n Reports Successfully Run. \n')
    exit()
    

if __name__ == '__main__':
    main()