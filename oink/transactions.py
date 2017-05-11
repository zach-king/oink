'''
File: transactions.py
'''

from __future__ import print_function
import re
from datetime import datetime

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db


def setup():
    '''
    Initial database setup; creates the `transactions` table
    '''
    cur = db.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id integer PRIMARY KEY AUTOINCREMENT,
            acct text,
            description text NOT NULL,
            amount integer NOT NULL,
            recorded_on text NOT NULL,
            FOREIGN KEY (acct) REFERENCES accounts (name)
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
        amount = input('Transaction amount: ')
        amount = float(re.sub(r'[^0-9\.]', '', amount))

        recorded_on = datetime.now().strftime('%Y-%m-%d')

        cur.execute('INSERT INTO transactions(acct, description, amount, recorded_on) \
            VALUES (?, ?, ?, ?)', (name, description, amount, recorded_on))
        db.commit()
        print('Transaction recorded')
        return

def list_transactions():
    '''
    Handler to list transactions for an account
    '''
    cur = db.cursor()
    cur.execute(
        'SELECT acct, description, amount, recorded_on FROM transactions ORDER BY recorded_on DESC')
    rows = cur.fetchall()
    print(tabulate(rows, headers=['Account', 'Description', 'Amount', 'Recorded On'], \
        tablefmt='psql'))
