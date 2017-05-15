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
            recorded_on text NOT NULL,
            FOREIGN KEY (acct)
                REFERENCES accounts (name)
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

        recorded_on = datetime.now().strftime('%Y-%m-%d')

        cur.execute('INSERT INTO transactions(acct, description, credit, amount, recorded_on) \
            VALUES (?, ?, ?, ?, ?)', (name, description, credit, amount, recorded_on))

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

def list_transactions():
    '''
    Handler to list transactions for an account
    '''
    cur = db.cursor()
    cur.execute(
        'SELECT acct, description, credit, amount, recorded_on FROM \
        transactions ORDER BY recorded_on DESC')
    rows = cur.fetchall()

    # Place (+/-) in front of amount in response to credit/debit
    new_rows = []
    for row in rows:
        str_amount = ''
        if row[2] == 1: # Credit
            str_amount = '-' + str(row[3])
        else:
            str_amount = '+' + str(row[3])
        new_rows.append(row[:2] + (str_amount,) + row[4:])

    print(tabulate(new_rows, headers=['Account', 'Description', 'Amount', 'Recorded On'], \
        tablefmt='psql'))
