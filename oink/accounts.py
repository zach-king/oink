#!/usr/bin/python3

'''
File: accounts.py
'''

from __future__ import print_function
import re
from datetime import datetime

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db
from .colorize import colorize, colorize_list
from .colorize import color_input, color_error, color_info, color_success


def setup():
    '''
    Initial database setup; creates the `accounts` table
    '''
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            acct_no text NOT NULL PRIMARY KEY,
            name text NOT NULL UNIQUE, 
            balance integer NOT NULL, 
            created_at text NOT NULL);
        ''')
    db.commit()


def list_accounts():
    '''
    Handler to list all accounts in the `accounts` table
    '''
    cur = db.cursor()
    cur.execute('SELECT acct_no, name, balance, created_at FROM accounts ORDER BY name')
    rows = cur.fetchall()
    headers = ['Account No.', 'Name', 'Balance', 'Created At']
    headers = colorize_list(headers, 'blue')
    print(tabulate(rows, headers=headers, tablefmt='psql'))


def rename():
    '''
    Handler to rename an existing account in the `accounts` table
    '''
    while True:
        # Get old account name
        oldname = input(color_input('Account name: '))

        # Validate
        if len(oldname) <= 0:
            print(color_info('Rename account cancelled.'))
            return

        cur = db.cursor()

        count = cur.execute('SELECT COUNT(*) FROM accounts \
            WHERE name = "{}"'.format(oldname)).fetchone()[0]

        # Check if still haven't found the account
        if count == 0:
            print(color_error('[error]') + ' Sorry, no account ' + \
                'was found by the name `{}`\n'.format(oldname))
            continue

        result = cur.execute('SELECT acct_no, name FROM accounts \
            WHERE name = "' + oldname + '"').fetchone()
        acct_no = result[0]

        # Get new name
        newname = input(color_input('New Account Name: '))

        # Validate
        if len(newname) <= 0:
            print(color_error('[error]') + ' Invalid account name')
            continue

        # Rename the old account
        cur.execute('UPDATE accounts SET name = "{}" WHERE acct_no = "{}"'.format(newname, acct_no))

        # Verify successfulness
        if cur.rowcount == 0:
            print(color_error('[error]') + ' Failed to rename the account.')
            return

        # Save the changes to the database
        db.commit()
        print(color_success(
            'The account `{}` was successfully renamed to `{}`'.format(result[1], newname)))
        return


def add_account(acct_no, acct_name, start_balance, created_on):
    '''
    Helper to add/insert a new account into the `accounts` table
    '''
    # Validation
    if acct_no == '' or acct_no is None or not acct_no.isdigit():
        raise ValueError('Invalid account number')
    if acct_name == '' or acct_name is None:
        raise ValueError('Invalid account name')
    if start_balance is None or start_balance < 0:
        raise ValueError('Invalid starting balance')
    if created_on is None or created_on == '':
        raise ValueError('Invalid creation date')

    cur = db.cursor()
    cur.execute('INSERT INTO accounts VALUES (?, ?, ?, ?)', \
        (acct_no, acct_name, start_balance, created_on))
    db.commit()


def add():
    '''
    Handler to add/insert a new account into the `accounts` table
    '''
    while True:
        # Read in the account number and validate
        acct_no = input(color_input('Account number: '))

        if len(acct_no) <= 0:
            print(color_info('Add account cancelled.'))
            return
        elif not acct_no.isdigit():
            print(color_error('[error]') + ' Only numerical digits are allowed.')
            continue

        # Validate acct_no
        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM accounts WHERE acct_no = ?', (acct_no,))
        result = cur.fetchone()
        count = result[0]

        if count > 0:
            print(color_error('[error]') + ' That account number already exists.')
            continue

        # Read in the account name and validate
        name = input(color_input('Account Name: '))

        if len(name) <= 0:
            print(color_info('Add account cancelled.'))
            return

        starting_balance = input(color_input('Starting balance: '))
        starting_balance = float(re.sub(r'[^0-9\.]', '', starting_balance))

        created_at = datetime.now().strftime('%Y-%m-%d')

        add_account(acct_no, name, starting_balance, created_at)
        print(color_success('Account created'))
        return


def delete(account_name):
    '''
    Handler to delete an existing account in the `accounts` table
    '''
    cur = db.cursor()

    while True:
        # Verify that account exists
        cur.execute('SELECT COUNT(*) FROM accounts WHERE name = "{}"'.format(account_name))
        count = cur.fetchone()[0]
        if count == 0:
            print(color_error('[error]') + \
                ' No account was found by the name `{}`'.format(account_name))
            return

        # Delete the account
        cur.execute('DELETE FROM accounts WHERE name = "{}"'.format(account_name))

        # Verify successfulness
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' Failed to delete the account `{}`'.format(account_name))
            return

        print(color_success('Deleted account `{}`'.format(account_name)))
        db.commit()
        return


def get_balance(acct):
    '''
    Quickly retrieve the balance of an account.
    If `acct` is a string, searches by name;
    if `acct` is an integer, searches by account number.
    If the account was not found, returns None.
    '''
    cur = db.cursor()

    if isinstance(acct, str):
        # Find by account name
        cur.execute('SELECT balance FROM accounts WHERE name = "{}"'.format(acct))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the name `{}`'.format(acct))
            return None
        return cur.fetchone()[0] # Return the balance, if found
    elif isinstance(acct, int):
        # Find by account number
        cur.execute('SELECT balance FROM accounts WHERE acct_no = {}'.format(acct))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the number `{}`'.format(acct))
            return None
        return cur.fetchone()[0] # Return the balance, if found

    return None


def set_balance(acct, new_balance):
    '''
    Quickly set the balance of an account.
    If `acct` is a string, searches by name;
    if `acct` is an integer, searches by account number.
    If the account was not found, returns False; otherwise, True.
    '''
    cur = db.cursor()

    if isinstance(acct, str):
        # Find by account name
        cur.execute('UPDATE accounts SET balance = {} WHERE name = "{}"'.format(new_balance, acct))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the name `{}`'.format(acct))
            return False
        return True
    elif isinstance(acct, int):
        # Find by account number
        cur.execute('UPDATE accounts SET balance = {} WHERE acct_no = {}'.format(new_balance, acct))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the number `{}`'.format(acct))
            return False
        return True

    return None


def exists(acct):
    '''Helper function to check if an account exists'''
    cur = db.cursor()
    return cur.execute('SELECT COUNT(*) FROM accounts WHERE name = "{}"'.format(
        acct)).fetchone()[0] != 0
