import logging
import datetime
import os
from pathlib import Path

LOG_FOLDER = "../Logs"

def check_for_log_folder():
    if(not os.path.exists(LOG_FOLDER)):
        os.mkdir(LOG_FOLDER)

def create_logfile():
    """Creates a new Log file with a date Identifier. If there is an existing log file with that identifier,
    the function adds an iterative number to the end of the file name until it gets to a file name that doesnt exist."""
    check_for_log_folder() # Checks for Log Folder, and creates one if its missing.
    date = str(datetime.datetime.now().strftime("%m_%d_%Y")) # sets date to a variable
    multiple = 1
    while True:  # Sets log file name, and checks if a log file bearing that name already exists. If it does, it iterates the name by one.
        logfile = ('Log_' + date + '_' + str(multiple))
        try:
            open(f'{LOG_FOLDER}/{logfile}.log', 'x')
            break
        except Exception as e:
            multiple += 1  # iterates the number at the end of the file

    logfile = (f'{LOG_FOLDER}/{logfile}.log') # sets logfile to the full filepath.
    logging.basicConfig(filename=logfile, level=logging.INFO) # sets the logging file as the newly created file.

create_logfile() # Creates Log File for program.

def write_to_log(type, message):
    """Outputs info string to the log file that is set upon initial script execution."""
    # on exception, This needs to write the traceback information as well as the failure message.
    type = type.lower()
    timestamped_message = str(datetime.datetime.now())+': '+message
    if type == 'info':
        logging.info(timestamped_message)  # Writes time and date as well as the info string to log file.
        print(timestamped_message)
    elif type == 'warning':
        logging.warning(timestamped_message)
        print(timestamped_message)
    elif type == 'error':
        logging.error(timestamped_message)
        print(timestamped_message)
    return


