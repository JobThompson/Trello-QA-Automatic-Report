from Config_Import import ProjectConfig
config = ProjectConfig()
from pandas import DataFrame, read_excel, ExcelWriter
import fnmatch


"""Local Imports"""
from API import get_boards, filter_boards, get_lists, get_list_selection, get_all_cards, get_cards_by_list, filter_lists
from LOG_local import create_logfile, write_to_log
LOGFILE = create_logfile()
# import GUI_local

"""Class Imports"""
# from TrelloList import TrelloList
from TrelloCard import TrelloCard
from TrelloReport import TrelloReport


"""BOARD FUNCTIONS"""
# def get_boards(): # Gets all the boards avaliable to the user that owns the API token and API key
#     board_ids = []
#     request = trello_get(f'members/me/boards?')
#     for i in request.json():
#         board_ids.append({'Name': i['name'], 'ID' : i['id']})
#     return board_ids

# def filter_boards(board_ids): # Only returns the board specified in the .env file by BOARD_NAME
#     for i in board_ids:
#         if i['Name'] == config.boardName:
#             return i

# def get_all_cards(board_information): # Gets all the cards for a given board # CURRENTLY UNUSED
#     board_id = board_information['ID']
#     request = trello_get(f'boards/{board_id}/cards?')
#     return request.json()


# """LIST FUNCTIONS"""
# def get_lists(board_information): # Gets the all of the lists from the passed in board
#     board_id = board_information['ID']
#     request = trello_get(f'boards/{board_id}/lists?')
#     return request.json()

# def get_list_selection(lists): # Gets the lists that analysis is needed on from the user, seperated by a comma.
#     for i in lists:
#         print(i['name'])
#     lists_to_parse = input('\nType the lists that you want information from, seperated by a comma:\n').lower()
#     list_selection = lists_to_parse.replace(' ', '').split(',')
#     print('')
#     return list_selection
    
# def filter_lists(lists, list_selection): 
#     # filters the input from the user to lowercase without spaces, and compares it to the passed in lists from the board, also filtered.
#     list_information = []
#     for i in lists:
#         name = i['name'].lower().replace(' ', '')
#         if name in list_selection:
#             list_information.append(i)
#     return list_information

# def get_cards_by_list(list_information): # Gets the cards from the lists that are passed in
#     cards_by_list = []
#     for i in list_information:
#         list_id = i['id']
#         request = trello_get(f'lists/{list_id}/cards?')
#         cards_by_list.append(TrelloList(i, request.json()))
#     return cards_by_list


"""CARD FUNCTIONS"""
def build_cards(cards_by_list): # Creates a Card_Object for each of the cards in the dictionary passed in, and assigns it to the list_objects card_objects value.
    for i in cards_by_list:
        cards = []
        for e in i.cards:
            cards.append(TrelloCard(e, i.name))
        i.card_objects = cards
    return

"""DATA ANALYSIS FUNCTIONS"""
def anaylze_cards(cards_by_list):
    reports = []
    for i in cards_by_list:
        report = TrelloReport(i.name, i.card_objects)
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
    
    month = [item for item in labels if item in config.months]
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
        data = read_excel((config.filePath + config.aggregateFileName), sheet_name='Main')
    except Exception as e:
        print('No historical file found, creating new file.')
        data = DataFrame([], columns=config.aggregateFileColumns)
    return data

def build_agg_report(reports):
    agreggate_dataframe = get_agg_data()
    with ExcelWriter(f'{config.filePath + config.aggregateFileName}') as writer:
        for i in reports:
            temp_agreggate_dataframe = DataFrame([[
                f'{config.today}',
                i.list_name,
                i.NumberOfCards,
                i.NumberOfTestCases,
                i.NumberOfBugCards,
                i.get_num_tested(),
                i.get_num_passed(),
                i.get_num_failed(),
                i.NumberOfBlockedCards,
                i.NumberOfFrontEndCards,
                i.NumberOfPassedFrontEndCards,
                i.NumberOfFailedFrontEndCards,
                i.NumberOfBackEndCards,
                i.NumberOfPassedBackEndCards,
                i.NumberOfFailedBackEndCards,
                i.get_num_of_retested(),
                i.NumberOfRetestedCardsPassed,
                i.NumberOfRetestedCardsFailed,
                i.get_num_awaiting_testing(),
                i.get_front_end_pending(),
                i.get_back_end_pending(),
                i.NumberOfCardsPendingRetest,
                i.NumberOfCardsNotInOriginSprint
            ]], columns=config.aggregateFileColumns)

            agreggate_dataframe = agreggate_dataframe.append(temp_agreggate_dataframe, ignore_index=True)
        agreggate_dataframe.to_excel(writer, sheet_name='Main', index=False)



def build_single_report(reports):
    with ExcelWriter(f'{config.filePath}{config.singleRunFileFolder}{config.today}- Single Run Report.xlsx') as writer:
        """Main Data"""
        single_run_dataframe = DataFrame([], columns=config.singleFileColumns)
        for i in reports:   
            temp_single_run_dataframe = DataFrame([[
                i.list_name,
                i.NumberOfCards,
                i.NumberOfTestCases,
                i.NumberOfBugCards,
                i.get_num_tested(),
                i.get_num_passed(),
                i.get_num_failed(),
                i.NumberOfBlockedCards,
                i.NumberOfFrontEndCards,
                i.NumberOfPassedFrontEndCards,
                i.NumberOfFailedFrontEndCards,
                i.NumberOfBackEndCards,
                i.NumberOfPassedBackEndCards,
                i.NumberOfFailedBackEndCards,
                i.get_num_of_retested(),
                i.NumberOfRetestedCardsPassed,
                i.NumberOfRetestedCardsFailed,
                i.get_num_awaiting_testing(),
                i.get_front_end_pending(),
                i.get_back_end_pending(),
                i.NumberOfCardsPendingRetest,
                i.NumberOfCardsNotInOriginSprint
            ]], columns=config.singleFileColumns)

            single_run_dataframe = single_run_dataframe.append(temp_single_run_dataframe, ignore_index=True)
        single_run_dataframe.to_excel(writer, sheet_name='Main', index=False)

        """Team Member Data"""
        team_member_dataframe = DataFrame([], columns=config.teamMemberColumns)
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
                ]], columns=config.teamMemberColumns)
                team_member_dataframe = team_member_dataframe.append(temp_team_member_dataframe, ignore_index=True)
        team_member_dataframe.to_excel(writer, sheet_name='Team Members', index=False)
    
        """Card Data"""
        card_dataframe = DataFrame([], columns=config.cardReportColumns)
        for e in reports:
            for i in e.card_objects:  
                temp_card_dataframe = DataFrame([[
                    i.list_name,
                    i.name,
                    i.status,
                    i.isInOriginList,
                    i.get_num_of_test_cases(),
                    i.passedTestCases,
                    i.failedTestCases,
                    i.passedRetestCases,
                    i.failedRetestCases,
                    i.testers,
                    i.url
                ]], columns=config.cardReportColumns)
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
def program():

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
    

# if __name__ == '__main__':
#     # write_to_log('info', 'Report Program Started.')
#     main()