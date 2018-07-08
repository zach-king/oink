'''
File: cli.py
'''

from __future__ import print_function
import os
import sys
import json

try:
    import readline
except:
    pass # possibility a user's build of python does not include readline

from . import accounts, db, router, transactions, budget, colorize, category
from .reporting import reports


TITLE = r'''
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
    '''
    Starting point. Ensures everything is setup and shows welcome message.

    '''
    installation_path = get_installation_path()
    db.connect(installation_path)

    # Setup the tables for the database
    accounts.setup()
    category.setup()
    transactions.setup()
    budget.setup()

    register_commands()
    show_welcome_message()

    try:
        router.wait()
    except KeyboardInterrupt:
        quit_oink()


def register_commands():
    '''
    Registers all commands with the router class. See router.register() for details.
    '''
    # Accounts commands
    router.register('header', 'Account', None)
    router.register('la', 'List bank accounts', accounts.list_accounts)
    router.register('aa', 'Add bank account', accounts.add)
    router.register('ra', 'Rename bank account', accounts.rename)
    router.register('da <id>', 'Delete bank account', accounts.delete)
    router.register('separator', None, None)

    # Transaction commands
    router.register('header', 'Transaction', None)
    router.register('at', 'Record a new transaction', transactions.new)
    router.register('lt [account] [num]', 'List transactions for an account; ' + \
        'defaults to all accounts and 10 transactions. ' + \
        'Use * to specify all.', transactions.list_transactions)
    router.register('ar <amount> <source_account> <destination_account>', 'Record a transfer ' + \
        'transaction between two accounts', transactions.add_transfer)
    router.register('et <id>', 'Edit a transaction', transactions.edit_transaction)
    router.register('dt <id>', 'Delete a transaction', transactions.delete_transaction)
    router.register('separator', None, None)

    # Category commands
    router.register('header', 'Categories', None)
    router.register('lc', 'List categories', category.list_all)
    router.register('ac <name>', 'Add new category', category.new)
    router.register('rc <name> <new_name>', 'Rename a category', category.rename)
    router.register('dc <id>', 'Delete a category and all its transactions', category.remove)
    router.register('separator', None, None)

    # Budget commands
    router.register('header', 'Budget', None)
    router.register('ab <account>', 'Add new budget for an account', budget.new)
    router.register('lb [mm] [yyyy]', 'List all budget categories for a month/year. ' + \
        'Defaults to current month and year', budget.list_budget)
    router.register('db <budget_id>', 'Delete a budget', budget.delete_budget)
    router.register('separator', None, None)

    router.register('header', 'Report', None)
    router.register('rep <file> <from_date> [to_date] [format]', 'Generate a report for a date range; ', reports.report)
    router.register('separator', None, None)

    router.register('q', 'Quit Oink', quit_oink)


def show_welcome_message():
    '''
    Clear screen and show the welcome to Oink message.
    '''
    # Clear screen on initial startup
    os.system('clear' if os.name == 'posix' else 'cls')

    # Set the color to gray
    colorize.set_color('gray')

    print(TITLE)
    print('Welcome to Oink, the CLI budgeting tools for nerds!')
    print('Type ? at any time to see what commands are available.')
    colorize.reset()


def quit_oink():
    '''
    Print a quit message, disconnect from the databse, and exit.
    '''
    print('\nThanks for using Oink!')
    db.disconnect()
    sys.exit(0)


def get_installation_path():
    '''
    Get the oink.db sqlite3 file path from ~/.oink config file. If the config
    file doesn't exist, ask for an installation path and create new config.

    The ~/.oink config file consists of a single line of text, which is the full
    path the the oink.db file.

    '''
    config_dir = os.path.join(os.path.expanduser('~'), '.oink')
    config_path = os.path.join(config_dir, 'config.json')

    setup_config()
    colorize.load_color_scheme()

    if os.path.isfile(config_path):
        with open(config_path, 'r') as fin:
            config = json.load(fin)

            if config['databasePath'] != "":
                return config['databasePath']
            else:
                while True:
                    print('Where would you like Oink to save its data?')
                    path = os.path.expanduser(input('> '))
                    if not os.path.isdir(path):
                        print(colorize.color_error('[error]') + ' That path doesn\'t exist.')
                        print('Please enter the full path to an existing folder.')
                    else:
                        config['databasePath'] = path
                        with open(config_path, 'w') as fout:
                            json.dump(config, fout, indent=4)
                        return path
    else:
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
        with open(config_path, 'w') as fout:
            default_config = {
                "colorscheme": {
                    "info": "blue",
                    "error": "red",
                    "success": "green",
                    "warning": "yellow",
                    "input": "cyan",
                    "headers": "blue",
                    "default": "white"
                },
                "databasePath": ""
            }
            json.dump(default_config, fout, indent=4)
        return get_installation_path()


def setup_config():
    """
    If the ~/.oink/ config directory has not been created
    yet, create it and create the default JSON config file in it
    """
    # Create the ~/.oink/ directory if it does not exist
    config_dir = os.path.join(os.path.expanduser('~'), '.oink')
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)

    config_path = os.path.join(config_dir, 'config.json')

    # If the config file does not exist, create it with the defaults
    if not os.path.isfile(config_path):
        with open(config_path, 'w') as fout:
            default_config = {
                "colorscheme": {
                    "info": "blue",
                    "error": "red",
                    "success": "green",
                    "warning": "yellow",
                    "input": "cyan",
                    "headers": "blue",
                    "default": "white"
                },
                "databasePath": ""
            }
            json.dump(default_config, fout, indent=4)
