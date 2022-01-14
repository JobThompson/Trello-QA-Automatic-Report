"""GUI Import"""
import PySimpleGUI as sg

""" GUI CONFIG """
sg.theme('Dark Grey 5')
menu_button_size_1 = (10, 4)
submenu_button_size = (19, 4)
submenu_button_size2 = (35, 2)
color1 = 'white'
color2 = 'black'
color3 = 'white'
color4 = 'black'


# def gui():
#     """Brings up the main menu for the program, with options for different GPU selections. Once a product stack is
#     selected, it calls for the submenu for the individual card. Once that choice is returned, the function returns
#     to the previous function."""
#     column1 = [
#                 [sg.Text('Select the Function You Want:')], 
#                 [gui_button('Add Test Case'), gui_button('Add Blocker')],
#                 [gui_button('Start Restesting'), gui_button('Add Retest Case')],
#                 [gui_button('Pass Card'), gui_button('Fail Card')]
#             ]

#     column2 = [
#                 [gui_button('Reports')], 
#                 [gui_button('Management Options')]
#             ]

#     layout = [[sg.Column(column1), sg.VSeparator(), sg.Column(column2)]]

#     window = sg.Window("Clayton County QA Report Program", layout, size=(400, 305), element_justification='c')
#     while True:
#         event, values = window.read()
#         if event == sg.WIN_CLOSED:
#             exit()
#         elif event == 'Reports':
#             window.close()
#             report_manager()
#             product = gui()
#             break
#         elif event == 'Custom URL':
#             window.close()
#             product = url_input()
#             break
#         else:
#             window.close()
#             product = display_list(choice)
#             break
#     return product



# def main():
#     """Main function that initiates the program. Calls GUI function for product choice, then checks for default login
#      credentials. If no credentials exist, it will prompt for them. If they do exist, it will launch the buy_product
#      function, and pass the default credentials on to the function. Once the buy_product returns an attempts variable,
#      it displays a success window and ends the program."""
#     try:
#         product = gui()  # opens GUI interface and gets product choice from user
#         # email, password, cvv, head = read_current_creds()  # gets credentials from current cookie
#         # if email == "" or password == "":  # if the creds are blank, prompts user for creds
#         #     while True:
#         #         email, password, cvv, head = credentials_manager()
#         #         if email == "" or password == "" or cvv == "":
#         #             write_to_log('Attempt to purchase without credentials.')
#         #             sg.popup_error('Credentials Are Required')
#         #         else:
#         #             print('Passed')
#         #             break
#         # else:
#         #     pass
#         # clear_current()  # clears the current cookie of all credentials
#         # attempts = buy_product(product, email, password, cvv, head)  # opens the bot, returns attempts
#         # item_purchased(attempts)  # opens success screen
#     except Exception as e:
#         # write_to_log(str(e))
#         # logging.error(traceback.format_exc())


class GUI:
    def __init__(self):
        return



    def gui_button(self, button_text):
        return sg.Button(button_text, size=menu_button_size_1, button_color=(color1, color2))

    def submenu_button(self, button_text):
        return sg.Button(button_text, size=submenu_button_size, button_color=(color3, color4))

    def submenu_button2(self, button_text):
        return sg.Button(button_text, size=submenu_button_size2, button_color=(color3, color4))

    def back_button(self):
        return sg.Button('Back', button_color=('black', 'darkred'), font=("Helvetica", 15), size=(7, 1))

    def submit_button(self):
        return sg.Submit(button_color=('black', 'green'), font=("Helvetica", 15), size=(7, 1))