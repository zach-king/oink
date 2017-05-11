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
    cur.execute('CREATE TABLE IF NOT EXISTS accounts (name, balance, created_at)')
    db.commit()


def list_accounts():
    '''
    Handler to list all accounts in the `accounts` table
    '''
    cur = db.cursor()
    cur.execute('SELECT name, balance, created_at FROM accounts ORDER BY name')
    rows = cur.fetchall()
    print(tabulate(rows, headers=['Name', 'Balance', 'Created At'], tablefmt='psql'))


def rename():
    '''
    Handler to rename an existing account in the `accounts` table
    '''
    while True:
        # Get old account name
        oldname = input('Account name: ')

        # Validate
        if len(oldname) <= 0:
            print('Invalid account name')
            continue

        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM accounts WHERE name = "' + oldname + '"')
        result = cur.fetchone()
        count = result[0]

        if count < 1:
            print('Sorry, no account was found by the name `' + oldname + '`')
            continue

        # Get new name
        newname = input('New Account Name: ')

        # Validate
        if len(newname) <= 0:
            print('Invalid account name')
            continue

        # Rename the old account
        cur.execute('UPDATE accounts SET name = "{}" WHERE name = "{}"'.format(newname, oldname))

        # Verify successfulness
        if cur.rowcount == 0:
            print('Failed to rename the account.')

        # Save the changes to the database
        db.commit()
        print('The account `{}` was successfully renamed to `{}`'.format(oldname, newname))
        return


def add():
    '''
    Handler to add/insert a new account into the `accounts` table
    '''
    while True:
        name = input('Account Name: ')

        if len(name) <= 0:
            print('Add account cancelled.')
            return

        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM accounts WHERE name = ?', (name,))
        result = cur.fetchone()
        count = result[0]

        if count > 0:
            print('That account name is already in use.')
            continue

        starting_balance = input('Starting balance: ')
        starting_balance = float(re.sub(r'[^0-9\.]', '', starting_balance))

        created_at = datetime.now().strftime('%Y-%m-%d')

        cur.execute('INSERT INTO accounts VALUES (?, ?, ?)', (name, starting_balance, created_at))
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
            continue

        # Delete the account
        cur.execute('DELETE FROM accounts WHERE name = "{}"'.format(account_name))

        # Verify successfulness
        if cur.rowcount == 0:
            print('Failed to delete the account `{}`'.format(account_name))
            return

        print('Deleted account `{}`'.format(account_name))
        db.commit()
        return
