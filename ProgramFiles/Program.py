import traceback
from Config_Import import ProjectConfig
from pandas import DataFrame, read_excel, ExcelWriter
import fnmatch

config_object = ProjectConfig()

"""Local Imports"""
from API import trello_get
from LOG_local import write_to_log

"""Class Imports"""
from TrelloCard import TrelloCard
from TrelloReport import TrelloReport
from TrelloList import TrelloList

"""BOARD FUNCTIONS"""
def get_boards(): # Gets all the boards avaliable to the user that owns the API token and API key
    board_ids = []
    try:
        request = trello_get(f'members/me/boards?')
        for i in request.json():
            board_ids.append({'Name': i['name'], 'ID' : i['id']})
        return board_ids
    except Exception:
        write_to_log('error', 'Unable to get Boards')

def filter_boards(board_ids): # Only returns the board specified in the .env file by BOARD_NAME
    for i in board_ids:
        if i['Name'] == config_object.boardName:
            return i
    write_to_log('error', 'Unable to find board specified in the .env file. Please doublecheck the board name.')

def get_all_cards(board_information): # Gets all the cards for a given board # CURRENTLY UNUSED
    try: 
        board_id = board_information['ID']
        request = trello_get(f'boards/{board_id}/cards?')
        return request.json()
    except Exception:
        write_to_log('error', 'Unable to get all cards from the board requested.')
    

"""LIST FUNCTIONS"""
def get_lists(board_information): # Gets the all of the lists from the passed in board
    try:
        board_id = board_information['ID']
        request = trello_get(f'boards/{board_id}/lists?')
        lists = []
        for i in request.json():
            lists.append(TrelloList(i))
        return lists
    except Exception:
        write_to_log('error', 'Unable to get lists')

def get_list_selection(lists): # Gets the lists that analysis is needed on from the user, seperated by a comma.
    try:
        for i in lists:
            print(i.name)
        response = input('\nType the lists that you want information from, seperated by a comma:\n').lower()
        write_to_log('info', f'report selection: {response}')
        user_selection = response.replace(' ', '').split(',')
        print('\n')
        return user_selection
    except Exception:
        write_to_log('error', 'Unable to get list selection from User.')
    
def filter_lists(lists, user_selection): 
    # filters the input from the user to lowercase without spaces, and compares it to the passed in lists from the board, also filtered.
    list_selection = []
    for i in lists:
        name = i.name.lower().replace(' ', '')
        if name in user_selection:
            list_selection.append(i)
    return list_selection

# def get_cards_by_list(list_selection, cards): # Gets the cards from the lists that are passed in
#     cards_by_list = []
#     for i in list_selection:
#         try:
#             list_id = i['id']
#             request = trello_get(f'lists/{list_id}/cards?')
#             cards_by_list.append(TrelloList(i, request.json()))
#         except Exception:
#             listname = i['Name']
#             write_to_log('error', f'Unable to get cards for {listname}')
#     return cards_by_list


"""CARD FUNCTIONS"""
def build_cards(cards, list_selection): # Creates a Card_Object for each of the cards in the dictionary passed in, and assigns it to the list_objects card_objects value.
    try:
        for i in cards:
            for e in list_selection:
                if i['idList'] == e.id:
                    e.card_objects.append(TrelloCard(i, e.name))
    except Exception as e:
        write_to_log('error', f'Unable to build cards')
        write_to_log('error', traceback.format_exc())
    return

"""DATA ANALYSIS FUNCTIONS"""
def analyze_cards(list_selection):
    reports = []
    try:
        for i in list_selection:
            report = TrelloReport(i.name, i.card_objects)
            for e in i.card_objects:
                labels = []
                report.NumberOfCards += 1
                for u in e.labels:
                    labels.append(u['name'])    
                report = get_passed_and_failed_stats(i, report, labels)
            write_to_log('info', f'Stats compiled for report: {i.name}')
            reports.append(report)
    except Exception:
        write_to_log('error', f'Unable to analyze cards.')
        write_to_log('error', traceback.format_exc())
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

    if 'Blocked' in labels and not any(entry in labels for entry in ['Failed', 'Passed']):
        report.NumberOfBlockedCards += 1

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

    if 'Retested' in labels and not any(entry in labels for entry in ['Passed','Failed']):
        report.NumberOfCardsPendingRetest += 1

    if f'Origin: {list.name}' not in labels:
        report.NumberOfCardsNotInOriginSprint += 1
    
    month = [item for item in labels if item in config_object.months]
    try:
        if month[0] in report.CardsByMonth:
            report.CardsByMonth[f'{month[0]}'] += 1
        else:
            report.CardsByMonth[f'{month[0]}'] = 1
    except Exception:
        pass

    year = fnmatch.filter(labels, '20*')
    try:
        if year[0] in report.CardsByYear:
            report.CardsByYear[f'{year[0]}'] += 1
        else:
            report.CardsByYear[f'{year[0]}'] = 1
    except Exception:
        pass

    try:
        if f'{month[0]} - {year[0]}' in report.CardsByMonthAndYear:
            report.CardsByMonthAndYear[f'{month[0]} - {year[0]}'] +=1
        else:
            report.CardsByMonthAndYear[f'{month[0]} - {year[0]}'] = 1
    except Exception:
        pass

    try:
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
                if 'Blocked' in labels and not any(entry in labels for entry in ['Failed', 'Passed']):
                    i.NumberOfBlockedCards += 1
    except Exception:
        write_to_log('error', f'Unable to get Team Member Statistics')
        write_to_log('error', traceback.format_exc())
    
    return report


def get_agg_data():
    try:
        data = read_excel((config_object.filePath + config_object.aggregateFileName), sheet_name='Main')
    except Exception as e:
        print('No historical file found, creating new file.')
        data = DataFrame([], columns=config_object.aggregateFileColumns)
    return data

def export_agg_report(reports):
    try:
        agreggate_dataframe = get_agg_data()
        with ExcelWriter(f'{config_object.filePath + config_object.aggregateFileName}') as writer:
            for i in reports:
                temp_agreggate_dataframe = DataFrame([[
                    f'{config_object.today}',
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
                ]], columns=config_object.aggregateFileColumns)

                agreggate_dataframe = agreggate_dataframe.append(temp_agreggate_dataframe, ignore_index=True)
            agreggate_dataframe.to_excel(writer, sheet_name='Main', index=False)
    except Exception:
        write_to_log('error', "unable to write to Main in Aggregate File, Please verify that the directory in the FILEPATH config exists.")
        write_to_log('error', traceback.format_exc())



def export_single_report(reports):
    with ExcelWriter(f'{config_object.filePath}{config_object.singleRunFileFolder}/{config_object.today} - Single Run Report.xlsx') as writer:
        """Main Data"""
        try: 
            single_run_dataframe = DataFrame([], columns=config_object.singleFileColumns)
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
                ]], columns=config_object.singleFileColumns)

                single_run_dataframe = single_run_dataframe.append(temp_single_run_dataframe, ignore_index=True)
            single_run_dataframe.to_excel(writer, sheet_name='Main', index=False)
        except Exception:
            write_to_log('error', "unable to write Main sheet in Single Run File")
            write_to_log('error', traceback.format_exc())

        """Team Member Data"""
        try:
            team_member_dataframe = DataFrame([], columns=config_object.teamMemberColumns)
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
                    ]], columns=config_object.teamMemberColumns)
                    team_member_dataframe = team_member_dataframe.append(temp_team_member_dataframe, ignore_index=True)
            team_member_dataframe.to_excel(writer, sheet_name='Team Members', index=False)
        except Exception:
            write_to_log('error', "unable to write Team Members sheet in Single Run File")
            write_to_log('error', traceback.format_exc())
    
        """Card Data"""
        try: 
            card_dataframe = DataFrame([], columns=config_object.cardReportColumns)
            for e in reports:
                for i in e.card_objects:  
                    temp_card_dataframe = DataFrame([[
                        i.list_name,
                        i.name,
                        i.status,
                        i.dev_team_assigned,
                        i.isInOriginList,
                        i.get_num_of_test_cases(),
                        i.passedTestCases,
                        i.failedTestCases,
                        i.passedRetestCases,
                        i.failedRetestCases,
                        i.testers,
                        i.url
                    ]], columns=config_object.cardReportColumns)
                    card_dataframe = card_dataframe.append(temp_card_dataframe, ignore_index=True)
            card_dataframe.to_excel(writer, sheet_name='Card Breakdown', index=False)
        except Exception:
            write_to_log('error', "unable to write Card Breakdown in Single Run File")
            write_to_log('error', traceback.format_exc())

def build_reports(report_selection, reports):
    if report_selection == 1:
        export_agg_report(reports)
    elif report_selection == 2:
        export_single_report(reports)
    elif report_selection == 3:
        export_agg_report(reports)
        export_single_report(reports)

def get_report_selection():
    options = {1:'Aggregate Only', 2:'Single File Only', 3:'Aggregate And Single File'}
    while True:
        for i in options:
            print(f'{i}. {options[i]}')
        response = input('\nSelect the Reports you would like to run: (1-3)\n')
        report_selection = int(response)
        if report_selection not in options:
            print('Selection Not Valid, Please selected a valid menu option.')
        else:
            break
        print('')
    write_to_log('info', f'{options[report_selection]} run selected.')
    return report_selection

    
"""MAIN"""
def program():
    board_ids = get_boards()
    board_information = filter_boards(board_ids)
    cards = get_all_cards(board_information)
    lists = get_lists(board_information)
    report_selection = get_report_selection()
    user_selection = get_list_selection(lists)
    list_selection = filter_lists(lists, user_selection)
    build_cards(cards, list_selection)
    reports = analyze_cards(list_selection)
    build_reports(report_selection, reports)
    print('\n Reports Successfully Run. \n')
    write_to_log('info', 'Reports Successfully Run.')
    return