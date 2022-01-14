from Program import program
import pprint
import time

def main():
    try: 
        program()
    except Exception as e:
        print('The program has run into a problem, please see error below: \n')
        pprint.pprint(e)
        input('Press Enter to exit.')
        exit()

if __name__ == '__main__':
    main()