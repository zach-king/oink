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


def setup():
    '''
    Initial database setup; creates the `accounts` table
    '''
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            acct_no integer PRIMARY KEY,
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
    print(tabulate(rows, headers=['Account No.', 'Name', 'Balance', 'Created At'], tablefmt='psql'))


def rename():
    '''
    Handler to rename an existing account in the `accounts` table
    '''
    while True:
        # Get old account name
        oldname = input('Account name or number: ')

        # Validate
        if len(oldname) <= 0:
            print('Rename account cancelled.')
            return

        cur = db.cursor()

        # Did the user enter an account number (most likely, can't tell for sure)?
        found = False
        acct_no = None
        result = None
        if oldname.isdigit():
            cur.execute('SELECT COUNT(*) FROM accounts WHERE acct_no = "' + oldname + '"')
            result = cur.fetchone()
            count = result[0]

            # Check if found by account number
            if count == 1:
                found = True
                acct_no = oldname

        # Try finding it by name
        if not found:
            cur.execute('SELECT COUNT(*) FROM accounts WHERE name = "' + oldname + '"')
            result = cur.fetchone()
            count = result[0]

            # Check if found by name
            if count == 1:
                found = True
                acct_no = result[0][0]

        # Check if still haven't found the account
        if not found:
            print('Sorry, no account was found by the name `' + oldname + '`\n')
            continue

        # Get new name
        newname = input('New Account Name: ')

        # Validate
        if len(newname) <= 0:
            print('Invalid account name')
            continue

        # Rename the old account
        cur.execute('UPDATE accounts SET name = "{}" WHERE acct_no = "{}"'.format(newname, acct_no))

        # Verify successfulness
        if cur.rowcount == 0:
            print('Failed to rename the account.')
            return

        # Save the changes to the database
        db.commit()
        print('The account `{}` was successfully renamed to `{}`'.format(result[0][1], newname))
        return


def add():
    '''
    Handler to add/insert a new account into the `accounts` table
    '''
    while True:
        # Read in the account number and validate
        acct_no = input('Account number: ')

        if len(acct_no) <= 0:
            print('Add account cancelled.')
            return
        elif not acct_no.isdigit():
            print('Only numerical digits are allowed.')
            continue

        acct_no = int(acct_no)

        # Read in the account name and validate
        name = input('Account Name: ')

        if len(name) <= 0:
            print('Add account cancelled.')
            return

        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM accounts WHERE acct_no = ?', (acct_no,))
        result = cur.fetchone()
        count = result[0]

        if count > 0:
            print('That account number already exists.')
            continue

        starting_balance = input('Starting balance: ')
        starting_balance = float(re.sub(r'[^0-9\.]', '', starting_balance))

        created_at = datetime.now().strftime('%Y-%m-%d')

        cur.execute('INSERT INTO accounts VALUES (?, ?, ?, ?)', \
            (acct_no, name, starting_balance, created_at))
        db.commit()
        print('Account created')
        return


def edit(account_name):
    '''
    Handler to edit an existing account in the `accounts` table
    '''
    print('TODO: edit account {0}'.format(account_name))


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
            print('Sorry, no account was found by the name `{}`'.format(account_name))
            return

        # Delete the account
        cur.execute('DELETE FROM accounts WHERE name = "{}"'.format(account_name))

        # Verify successfulness
        if cur.rowcount == 0:
            print('Failed to delete the account `{}`'.format(account_name))
            return

        print('Deleted account `{}`'.format(account_name))
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
            print('No account was found by the name `{}`'.format(acct))
            return None
        return cur.fetchone()[0] # Return the balance, if found
    elif isinstance(acct, int):
        # Find by account number
        cur.execute('SELECT balance FROM accounts WHERE acct_no = {}'.format(acct))
        if cur.rowcount == 0:
            print('No account was found by the number `{}`'.format(acct))
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
            print('No account was found by the name `{}`'.format(acct))
            return False
        return True
    elif isinstance(acct, int):
        # Find by account number
        cur.execute('UPDATE accounts SET balance = {} WHERE acct_no = {}'.format(new_balance, acct))
        if cur.rowcount == 0:
            print('No account was found by the number `{}`'.format(acct))
            return False
        return True

    return None
