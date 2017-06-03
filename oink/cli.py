'''
File: cli.py
'''

from __future__ import print_function
import os
import sys

from . import accounts, db, router, transactions, budget, reports


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
    router.register('da <name>', 'Delete bank account', accounts.delete)
    router.register('separator', None, None)

    # Transaction commands
    router.register('header', 'Transaction', None)
    router.register('at', 'Record a new transaction', transactions.record_transaction)
    router.register('lt [account] [num]', 'List transactions for an account; ' + \
        'defaults to all accounts and 10 transactions. ' + \
        'Use * to specify all.', transactions.list_transactions)
    router.register('ar [source] [dest] [amount]', 'Record a transfer ' + \
        'transaction between two accounts', transactions.add_transfer)
    router.register('et <id>', 'Edit a transaction', transactions.edit_transaction)
    router.register('dt <id>', 'Delete a transaction', transactions.delete_transaction)
    router.register('separator', None, None)

    # Budget commands
    router.register('header', 'Budget', None)
    router.register('ab', 'Add budget category', budget.create_budget)
    router.register('lb [mm] [yyyy]', 'List all budget categories for a month. ' + \
        'Defaults to current month', budget.list_budget)
    router.register('sb <category> <amount>', 'Set budget ' + \
        'category amount', budget.set_budget)
    router.register('rb <oldname> <newname>', 'Rename a budget category', budget.rename_budget)
    router.register('db <category>', 'Delete a budget category', budget.delete_budget)
    router.register('separator', None, None)

    router.register('header', 'Report', None)
    router.register('rep <account> <file> [format]', 'Generate a report', reports.report)
    router.register('separator', None, None)

    router.register('q', 'Quit Oink', quit_oink)


def show_welcome_message():
    '''
    Clear screen and show the welcome to Oink message.
    '''
    # Clear screen on initial startup
    os.system('clear' if os.name == 'posix' else 'clr')

    print(TITLE)
    print('Welcome to Oink, the CLI budgeting tools for nerds!')
    print('Type ? at any time to see what commands are available.')


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
    config_path = os.path.join(os.path.expanduser('~'), '.oink')

    if os.path.isfile(config_path):
        with open(config_path, 'r') as fin:
            return fin.read()

    else:
        while True:
            print('Where would you like Oink to save its data?')
            path = input('> ')
            if not os.path.isdir(path):
                print('That path doesn\'t exist.')
                print('Please enter the full path to an existing folder.')
            else:
                with open(config_path, 'w') as fout:
                    fout.write(path)
                return path
