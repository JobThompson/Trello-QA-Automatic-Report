from GUI_local_test import GUI, gui_button, sg

def main():
    gui = GUI('Test Window', title_span = [sg.Text('Select the Function You Want:', key='-HEADER-')], buttons=[ 
                [gui_button('Trello Functions', '-getTrelloFunctions-'), gui_button('Management','-getManagement-')]])
    while True:
        gui.read_event()
    event, values = gui.window.read()


if __name__ == '__main__':
    main()