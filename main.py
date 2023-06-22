from ProgramFiles.Program import program
import pprint
import traceback
from ProgramFiles.LOG_local import write_to_log

def main():
    try: 
        write_to_log('info', 'Program Started')
        program()
        write_to_log('info', 'Program Ended')
        input('Press Enter to exit.')
    except Exception:
        write_to_log('error', 'The program ran into a problem.')
        write_to_log('error', traceback.format_exc())
        print('The program has run into a problem, please see error below: \n')
        pprint.pprint(traceback.format_exc())
        input('Press Enter to exit.')

if __name__ == '__main__':
    main()