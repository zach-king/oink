#!/usr/bin/env python3

"""
File: accounts.py
"""

from __future__ import print_function
import re
from datetime import datetime
import locale

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db, utils
from .colorize import colorize, colorize_headers, colorize_list
from .colorize import color_input, color_error, color_info, color_success


def setup():
    """
    Initial database setup; creates the `accounts` table
    """
    locale.setlocale(locale.LC_ALL, '')
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id integer NOT NULL PRIMARY KEY,
            account_number text NOT NULL,
            name text NOT NULL UNIQUE,
            balance integer NOT NULL,
            created_at text NOT NULL);
        ''')
    db.commit()


def list_accounts():
    """
    Handler to list all accounts in the `accounts` table
    """
    cur = db.cursor()
    cur.execute('''SELECT id, account_number, name, balance, created_at
                   FROM accounts ORDER BY name''')
    rows = cur.fetchall()

    new_rows = []

    for acct in rows:
        balance = acct[3] / 100
        if balance < 0:
            balance = colorize('-' + locale.currency(-1 * balance, grouping=True), 'red')
        else:
            balance = colorize(locale.currency(balance, grouping=True), 'green')
        new_rows.append(colorize_list(acct[:3], ['white', 'white', 'cyan']) + [balance,] + colorize_list(acct[4:], ['yellow']))
    headers = colorize_headers(['ID', 'Account No.', 'Name', 'Balance', 'Created At'])
    print(tabulate(new_rows, headers=headers, tablefmt='grid'))


def rename():
    """
    Handler to rename an existing account in the `accounts` table
    """
    while True:
        # Get old account id
        account_id = input(color_input('Account ID: '))

        # Validate
        try:
            account_id = int(account_id)
        except:
            print(color_info('Rename account cancelled.'))
            return

        cur = db.cursor()

        count = cur.execute('SELECT COUNT(*) FROM accounts \
            WHERE id = ?', [account_id,]).fetchone()[0]

        # Check if still haven't found the account
        if count == 0:
            print(color_error('[error]') + ' Sorry, no account ' + \
                'was found with that ID\n')
            continue

        acct_no, old_name = cur.execute('SELECT account_number, name FROM accounts \
            WHERE id = ?', [account_id,]).fetchone()

        # Get new name
        newname = input(color_input('New Account Name: '))

        # Validate
        if len(newname) <= 0:
            print(color_error('[error]') + ' Invalid account name')
            continue

        # Rename the old account
        cur.execute('UPDATE accounts SET name = ? WHERE id = ?',
                    [newname, account_id,])

        # Verify successfulness
        if cur.rowcount == 0:
            print(color_error('[error]') + ' Failed to rename the account.')
            return

        # Save the changes to the database
        db.commit()
        print(color_success(
            'The account `{}` was successfully renamed to `{}`'.format(old_name, newname)))
        return


def add_account(acct_no, acct_name, start_balance):
    """
    Helper to add/insert a new account into the `accounts` table
    """
    # Validation
    if not acct_no or not acct_no.isdigit():
        raise ValueError('Invalid account number')
    if not acct_name:
        raise ValueError('Invalid account name')
    if start_balance is None or start_balance == '' or start_balance < 0:
        raise ValueError('Invalid starting balance')

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur = db.cursor()
    cur.execute('''INSERT INTO accounts (account_number, name, balance, created_at)
                   VALUES (?, ?, ?, ?)''',
                   (acct_no, acct_name, start_balance, created_at))
    db.commit()


def add():
    """
    Handler to add/insert a new account into the `accounts` table
    """
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
        cur.execute('SELECT COUNT(*) FROM accounts WHERE account_number = ?', (acct_no,))
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
        starting_balance = utils.strpmoney(starting_balance)

        add_account(acct_no, name, starting_balance)
        print(color_success('Account created'))
        return


def delete(account_id):
    """
    Handler to delete an existing account in the `accounts` table
    """
    cur = db.cursor()

    while True:
        # Verify that account exists
        cur.execute('SELECT COUNT(*) FROM accounts WHERE id = ?', (account_id,))
        count = cur.fetchone()[0]
        if count == 0:
            print(color_error('[error]') + \
                ' No account was found by the ID `{}`'.format(account_id))
            return

        # Confirm deletion
        conf = input(color_input('Are you sure you want to delete this account? [y/n] '))
        if conf.lower() != 'y':
            print(color_info('Aborted account deletion'))
            return

        # Delete the account
        cur.execute('DELETE FROM accounts WHERE id = ?', (account_id,))

        # Verify successfulness
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' Failed to delete the account (ID: {})'.format(account_id))
            return

        print(color_success('Deleted account (ID: {})'.format(account_id)))
        db.commit()
        return


def get_balance(acct):
    """
    Quickly retrieve the balance of an account.
    If `acct` is a string, searches by name;
    if `acct` is an integer, searches by account id.
    If the account was not found, returns None.
    """
    cur = db.cursor()

    if isinstance(acct, str):
        # Find by account name
        cur.execute('SELECT balance FROM accounts WHERE name = ?', (acct,))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the name `{}`'.format(acct))
            return None
        return cur.fetchone()[0] # Return the balance, if found
    elif isinstance(acct, int):
        # Find by account number
        cur.execute('SELECT balance FROM accounts WHERE id = ?', (acct,))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the ID `{}`'.format(acct))
            return None
        return cur.fetchone()[0] # Return the balance, if found

    return None


def set_balance(acct, new_balance):
    """
    Quickly set the balance of an account.
    If `acct` is a string, searches by name;
    if `acct` is an integer, searches by account ID.
    If the account was not found, returns False; otherwise, True.
    """
    cur = db.cursor()

    if isinstance(acct, str):
        # Find by account name
        cur.execute('UPDATE accounts SET balance = ? WHERE name = ?', (new_balance, acct))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the name `{}`'.format(acct))
            return False
        return True
    elif isinstance(acct, int):
        # Find by account number
        cur.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_balance, acct))
        if cur.rowcount == 0:
            print(color_error('[error]') + \
                ' No account was found by the ID `{}`'.format(acct))
            return False
        return True

    return None


def exists(acct):
    """
    Helper function to check if an account exists
    """
    cur = db.cursor()
    return cur.execute('SELECT COUNT(*) FROM accounts WHERE id = ?', (acct,)).fetchone()[0] != 0


class Account(object):
    def __init__(self, id, account_number, name, balance, created_at):
        self.id = id
        self.account_number = account_number
        self.name = name
        self.balance = balance
        self.created_at = created_at


def get(account_id):
    cur = db.cursor()
    acct = cur.execute('SELECT id, account_number, name, balance, created_at \
        FROM accounts WHERE id = ?', (account_id,)).fetchone()
    return Account(*acct)


def all():
    cur = db.cursor()
    rows = cur.execute('SELECT id, account_number, name, balance, created_at \
        FROM accounts ORDER BY id').fetchall()
    accounts = [Account(*row) for row in rows]
    return accounts
