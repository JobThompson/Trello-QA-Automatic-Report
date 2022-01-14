import os
import sys
import json
import pprint
from datetime import date

try:
    with open(os.path.join(sys.path[0],"config_file.json"), "r") as f:
        json_config = json.load(f)

except Exception as e:
    print('Unable to load config, See error below: \n')
    pprint.pprint(e)
    exit()


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
        'December'
        ]

SINFLE_FILE_COLUMNS = [
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

TEAM_MEMBER_COLUMNS = [
                        'Sprint',
                        'Name',
                        'Total Cards Tested',
                        'Cards Passed',
                        'Cards Failed',
                        'Cards Retested',
                        'Cards Pending',
                        'Blocked Cards'
                    ]

AGGREGATE_FILE_COLUMNS = [
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

CARD_REPORT_COLUMNS = [
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

class ProjectConfig:
    def __init__(self):
        self.teamMembers = json_config['TEAM_MEMBERS']
        self.boardName = json_config['BOARD_NAME']
        self.filePath = json_config['FILEPATH']
        self.aggregateFileName = json_config['AGG_FILE_NAME']
        self.singleRunFileFolder = json_config['SINGLE_FILE_FOLDER']
        self.months = MONTHS
        self.singleFileColumns = SINFLE_FILE_COLUMNS
        self.aggregateFileColumns = AGGREGATE_FILE_COLUMNS
        self.teamMemberColumns = TEAM_MEMBER_COLUMNS
        self.cardReportColumns = CARD_REPORT_COLUMNS
        self.today = date.today() 
