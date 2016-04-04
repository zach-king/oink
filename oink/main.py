import os

from . import data
from . import handlers


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


COMMANDS = [
    ['ls', 'List budget', handlers.ls],
    ['set', 'Set budget for a category', handlers.set],
    ['track', 'Track expenses', handlers.track],
    ['income', 'Add income', handlers.income],
    ['quit', 'Save and quit', handlers.quit]
]


def init():
    """
    Starting point. Ensures everything is setup and shows welcome message.

    """
    installation_path = get_installation_path()
    # TODO get starting balance
    data.load(installation_path)
    show_welcome_message()
    try:
        listen()
    except KeyboardInterrupt:
        handlers.quit()


def handle_command(command):
    if command == '?':
        for c in COMMANDS:
            print('{0} | {1}'.format(c[0].ljust(6), c[1]))

    else:
        for c in COMMANDS:
            if c[0] == command:
                return c[2]()

        print('Invalid command. Type ? to see whats available.')


def listen():
    while True:
        print('') # Whitespace
        command = input('> ')
        print('') # More whitespace (oh baby!)
        handle_command(command)
                    

def show_welcome_message():
    # Clear screen on initial startup
    os.system('clear' if os.name == 'posix' else 'clr')

    print(TITLE)
    print('Welcome to Oink, the CLI budgeting tools for nerds!')
    print('Type ? at any time to see what commands are available.')


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