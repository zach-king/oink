import os
import sys

from . import accounts, db, router


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

    router.register('ls accounts', 'List bank accounts', accounts.ls)
    router.register('add account', 'Add bank account', accounts.add)
    router.register('edit account <name>', 'Edit bank account', accounts.edit)
    router.register('del account <name>', 'Delete bank account', accounts.delete)

    router.register('quit', 'Quit Oink', quit_oink)

    # Clear screen on initial startup
    os.system('clear' if os.name == 'posix' else 'clr')

    print(TITLE)
    print('Welcome to Oink, the CLI budgeting tools for nerds!')
    print('Type ? at any time to see what commands are available.')

    try:
        router.wait()
    except KeyboardInterrupt:
        quit_oink()


def quit_oink(signal=None, frame=None):
    print('\nThanks for using Oink!')
    sys.exit(0)


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
