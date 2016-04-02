import re
from datetime import datetime

from tabulate import tabulate

from . import db


def setup():
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS accounts (name, balance, created_at)')
    db.commit()


def ls():
    c = db.cursor()    
    c.execute('SELECT name, balance, created_at FROM accounts ORDER BY name')
    rows = c.fetchall()
    print(tabulate(rows, headers=['Name', 'Balance', 'Created At'], tablefmt='psql'))


def add():
    while True:
        name = input('Account Name: ')

        if len(name) <= 0:
            print('Add account cancelled.')
            return

        c = db.cursor()
        c.execute('SELECT COUNT(*) FROM accounts WHERE name = ?', (name,))
        result = c.fetchone()
        count = result[0]

        if count > 0:
            print('That account name is already in use.')
            continue

        starting_balance = input('Starting balance: ')
        starting_balance = float(re.sub(r'[^0-9\.]', '', starting_balance))

        created_at = datetime.now().strftime('%Y-%m-%d')

        c.execute('INSERT INTO accounts VALUES (?, ?, ?)', (name, starting_balance, created_at))
        db.commit()
        print('Account created')
        return


def edit(account_name):
    print('TODO: edit account {0}'.format(account_name))


def delete(account_name):
    print('TODO: delete account {0}'.format(account_name))
