import os

from . import accounts, budget, db, menu, transactions


TITLE = '''
 $$$$$$\  $$\           $$\       
$$  __$$\ \__|          $$ |      
$$ /  $$ |$$\ $$$$$$$\  $$ |  $$\ 
$$ |  $$ |$$ |$$  __$$\ $$ | $$  |
$$ |  $$ |$$ |$$ |  $$ |$$$$$$  / 
$$ |  $$ |$$ |$$ |  $$ |$$  _$$<  
 $$$$$$  |$$ |$$ |  $$ |$$ | \$$\ 
 \______/ \__|\__|  \__|\__|  \__|
 '''


def main():
    """
    Starting point. Ensures everything is setup and shows welcome message.

    """
    installation_path = get_installation_path()
    db.path = os.path.join(installation_path, 'oink.db')
    welcome()


def welcome():
    menu.clear_screen()

    print(TITLE)
    print('Welcome to Oink, the CLI budgeting tool for nerds!')
    print('Type ? to any time to see what commands are available.')

    menu.register_view('accounts', 'View and manage accounts', accounts.commands)
    menu.register_view('budget', 'View and manage budget', budget.commands)
    menu.register_view('transactions', 'View and manage transactions', transactions.commands)
    menu.listen()


def exit_oink():
    exit(0)


def get_installation_path():
    """
    Get the oink.db sqlite3 file path from ~/.oink config file. If the config
    file doesn't exist, ask for an installation path and create new config.

    The ~/.oink config file consists of a single line of text, which is the full
    path the the oink.db file.

    """
    config_path = os.path.join(os.path.expanduser('~'), '.oink')

    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            return f.read()

    else:
        while True:
            print('Where would you like Oink to save its data?')
            path = input('> ')
            if not os.path.isdir(path):
                print('That path doesn\'t exist.')
                print('Please enter the full path to an existing folder.')
            else:
                with open(config_path, 'w') as f:
                    f.write(path)
                return path
