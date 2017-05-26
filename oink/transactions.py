'''
File: transactions.py
'''

from __future__ import print_function
import re
from datetime import datetime

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db, accounts


def setup():
    '''
    Initial database setup; creates the `transactions` table
    '''
    cur = db.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id integer PRIMARY KEY AUTOINCREMENT,
            acct text NOT NULL,
            description text NOT NULL,
            credit integer NOT NULL,
            amount integer NOT NULL,
            budget_category text NOT NULL,
            recorded_on text NOT NULL,
            FOREIGN KEY (acct)
                REFERENCES accounts (name)
                ON UPDATE CASCADE
                ON DELETE CASCADE,
            FOREIGN KEY (budget_category)
                REFERENCES budget_categories (category_name)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );
        ''')
    db.commit()

def record_transaction():
    '''
    Handler to record a new transaction in a given account
    '''
    while True:
        name = input('Account Name: ')

        if len(name) <= 0:
            print('Record transaction cancelled.')
            return

        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM accounts WHERE name = ?', (name,))
        result = cur.fetchone()
        count = result[0]

        if count <= 0:
            print('Sorry, no account was found under the name `{}`.'.format(name))
            continue

        description = input('Transaction description: ')
        if len(description) <= 0:
            print('Record transaction cancelled.')
            return

        credit = input('Credit (withdrawal) or Debit (deposit)? (C/D): ')
        if len(credit) <= 0:
            print('Record transaction cancelled.')
            return
        if credit.lower() == 'c':
            credit = 1
        elif credit.lower() == 'd':
            credit = 0
        else:
            print('Incorrect entry for credit/debit.')
            continue

        amount = input('Transaction amount: ')
        if len(amount) <= 0:
            print('Record transaction cancelled.')
            return
        amount = float(re.sub(r'[^0-9\.]', '', amount))

        category = input('Budget category: ')
        if len(category) <= 0:
            print('Record transaction cancelled.')
            return
        cur.execute('SELECT * FROM budget_categories WHERE category_name = "{}"'.format(category))
        if cur.rowcount == 0:
            print('Sorry, no budget category was found under the name `{}`'.format(category))
            continue

        recorded_on = datetime.now().strftime('%Y-%m-%d')

        cur.execute('INSERT INTO transactions(acct, description, credit, amount, budget_category, recorded_on) \
            VALUES (?, ?, ?, ?, ?, ?)', (name, description, credit, amount, category, recorded_on))

        if cur.rowcount == 0:
            print('Failed to record transaction.')
            return

        # Now withdraw or deposit from the account as recorded
        prev_balance = accounts.get_balance(name)
        new_balance = 0
        if credit == 1:
            new_balance = prev_balance - amount
        else:
            new_balance = prev_balance + amount

        # Set the new balance
        success = accounts.set_balance(name, new_balance)

        if success:
            db.commit()
            print('Transaction recorded')
            return

        print('Failed to update balance.')
        return

def list_all_transactions():
    '''
    Handler to list transactions for all accounts
    '''
    cur = db.cursor()
    cur.execute(
        'SELECT trans_id, acct, description, credit, amount, budget_category, recorded_on FROM transactions ORDER BY recorded_on DESC')
    rows = cur.fetchall()

    # Place (+/-) in front of amount in response to credit/debit
    new_rows = []
    for row in rows:
        str_amount = ''
        if row[3] == 1: # Credit
            str_amount = '-' + str(row[4])
        else:
            str_amount = '+' + str(row[4])
        new_rows.append(row[:3] + (str_amount,) + row[5:])

    print(tabulate(new_rows, headers=['Transaction #', 'Account', 'Description', 'Amount', 'Category', 'Recorded On'], \
        tablefmt='psql'))

def list_transactions(acct):
    '''
    Handler to list transactions for a given account.
    '''
    cur = db.cursor()
    cur.execute('SELECT * FROM accounts WHERE name = "{}"'.format(acct))
    if cur.rowcount == 0:
        print('No account was found by the name `{}`'.format(acct))
        return

    cur.execute(
        'SELECT trans_id, acct, description, credit, amount, budget_category, recorded_on \
        FROM transactions WHERE acct = "{}" ORDER BY recorded_on DESC'.format(acct))
    rows = cur.fetchall()

    # Place (+/-) in front of amount in response to credit/debit
    new_rows = []
    for row in rows:
        str_amount = ''
        if row[3] == 1: # Credit
            str_amount = '-' + str(row[4])
        else:
            str_amount = '+' + str(row[4])
        new_rows.append(row[:3] + (str_amount,) + row[5:])

    print(tabulate(new_rows, headers=['Transaction #', 'Account', 'Description', 'Amount', 'Category', 'Recorded On'], \
        tablefmt='psql'))
