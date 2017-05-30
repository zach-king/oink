'''
File: transactions.py
'''

from __future__ import print_function
import re
from datetime import datetime

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db, accounts, budget


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
            budget_category text,
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

def _add_transaction(acct, desc, credit, amount, category):
    '''Helper function for adding a transaction'''
    cur = db.cursor()
    recorded_on = datetime.now().strftime('%Y-%m-%d')
    if category not in ('', 'null', 'NULL', None):
        cur.execute('INSERT INTO transactions(acct, description, credit, amount, budget_category, recorded_on) \
            VALUES ("{}", "{}", {}, {}, "{}", "{}")'.format(acct, desc, credit, amount, category, recorded_on))
    else:
        cur.execute('INSERT INTO transactions(acct, description, credit, amount, budget_category, recorded_on) \
            VALUES ("{}", "{}", {}, {}, NULL, "{}")'.format(acct, desc, credit, amount, recorded_on))

    if cur.rowcount == 0:
        print('Failed to record transaction.')
        return

    # Now withdraw or deposit from the account as recorded
    prev_balance = accounts.get_balance(acct)
    new_balance = 0
    if credit == 1:
        new_balance = prev_balance - amount
    else:
        new_balance = prev_balance + amount

    # Set the new balance
    success = accounts.set_balance(acct, new_balance)

    return success

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
        if category.lower() in ('', 'none', 'null', 'n/a'):
            category = 'NULL'
        else:
            cur.execute('SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}"'.format(category))
            if cur.fetchone()[0] == 0:
                print('Sorry, no budget category was found under the name `{}`'.format(category))
                continue

        # Call the helper function
        success = _add_transaction(name, description, credit, amount, category)
        if success:
            db.commit()
            print('Transaction recorded')
            return

        print('Failed to update balance.')
        return

def list_all_transactions(num=10):
    '''
    Handler to list transactions for all accounts
    '''
    limit_inject = ''
    if num not in (None, '*'):
        limit_inject = 'LIMIT ' + str(num)

    cur = db.cursor()
    cur.execute(
        'SELECT trans_id, acct, description, credit, amount, \
        budget_category, recorded_on FROM transactions ORDER BY recorded_on DESC \
        {}'.format(limit_inject))
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

    print(tabulate(new_rows, headers=['Transaction #', 'Account', \
    'Description', 'Amount', 'Category', 'Recorded On'], \
        tablefmt='psql'))

def list_transactions(acct=None, num=10):
    '''
    Handler to list transactions for a given account.
    '''
    if acct in (None, '*'):
        list_all_transactions(num)
        return

    limit_inject = ''
    if num not in (None, '*'):
        limit_inject = 'LIMIT ' + str(num)

    cur = db.cursor()
    cur.execute('SELECT * FROM accounts WHERE name = "{}"'.format(acct))
    if cur.rowcount == 0:
        print('No account was found by the name `{}`'.format(acct))
        return

    cur.execute(
        'SELECT trans_id, acct, description, credit, amount, budget_category, \
        recorded_on FROM transactions WHERE acct = "{}" ORDER BY recorded_on \
        DESC {}'.format(acct, limit_inject))
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

    print(tabulate(new_rows, headers=['Transaction #', 'Account', \
        'Description', 'Amount', 'Category', 'Recorded On'], \
        tablefmt='psql'))


def add_transfer(source_acct=None, dest_acct=None, amount=None):
    '''Handler for adding a transfer transaction between two accounts'''
    # Check for optargs and validate data
    cur = db.cursor()
    accts = [acct[0] for acct in cur.execute('SELECT name FROM accounts')]
    if source_acct is None:
        source_acct = input('Source account name: ')
    if source_acct == '':
        print('Transfer transaction cancelled.')
        return
    if source_acct not in accts:
        print('The source account `{}` does not exist.'.format(source_acct))
        return

    if dest_acct is None:
        dest_acct = input('Destination account name: ')
    if dest_acct == '':
        print('Transfer transaction cancelled.')
        return
    if dest_acct not in accts:
        print('The destination account `{}` does not exist.'.format(dest_acct))
        return

    if amount is None:
        amount = input('Amount to transfer: ')
    try:
        amount = float(amount)
    except ValueError:
        print('The amount must be a number!')
        return
    else:
        if amount <= 0:
            print('The amount must be greater than zero!')
            return

    # Make the two transactions on the accounts
    success = _add_transaction(source_acct, 'Transfer to `{}`'.format(dest_acct), 1, amount, None)
    success = success and _add_transaction(dest_acct, 'Transfer from `{}`'.format(source_acct), 0, amount, None)

    if success:
        print('Transfer from `{}` to `{}` recorded.'.format(source_acct, dest_acct))
        db.commit()
        return

    print('Failed to record transfer transaction from `{}` to `{}`.'.format(source_acct, dest_acct))


def delete_transaction(trans_id):
    '''Handler for the delete a transaction command'''
    # Validate the transaction id
    cur = db.cursor()
    if trans_id == '' or trans_id is None:
        print('Delete transaction cancelled.')
        return

    try:
        trans_id = int(trans_id)
    except ValueError:
        print('Transaction ID must be an integer!')
        return

    rows = cur.execute('SELECT COUNT(*) FROM transactions WHERE trans_id = {}'.format(trans_id)).fetchone()
    if rows[0] != 1:
        print('No transaction was found with ID `{}`'.format(trans_id))
        return

    # Counter the transaction effect
    transaction = cur.execute('SELECT acct, credit, amount, budget_category FROM transactions \
        WHERE trans_id = {}'.format(trans_id)).fetchone()
    account = transaction[0]
    amount = transaction[2]
    amount *= -1 if transaction[1] == 0 else 1
    category = transaction[3]

    # Update the balance of the account
    accounts.set_balance(account, accounts.get_balance(account) + amount)

    # Valid and exists so delete
    cur.execute('DELETE FROM transactions WHERE trans_id = {}'.format(trans_id))
    if cur.execute('SELECT COUNT(*) FROM transactions WHERE trans_id = {}'.format(trans_id)).fetchone()[0] != 0:
        print('Failed to delete transaction.')
        return

    print('Transaction deleted.')
    db.commit()


def _edit_transaction(trans_id, description=None, credit=None, amount=None, budget_category=None):
    '''Helper function for updating a transaction record'''
    cur = db.cursor()
    # Get current record
    transaction = cur.execute('SELECT description, credit, amount, budget_category FROM \
        transactions WHERE trans_id = {}'.format(trans_id)).fetchone()

    if description is None:
        description = transaction[0]
    if credit is None:
        credit = transaction[1]
    if amount is None:
        amount = transaction[2]
    if budget_category is None:
        budget_category = transaction[3]

    # Update where different
    cur.execute('UPDATE transactions SET description = "{}", credit = {}, \
        amount = {}, budget_category = "{}" WHERE trans_id = {}'.format(
            description, credit, amount, budget_category, trans_id
        ))
    if cur.rowcount == 1:
        db.commit()
        return True
    return False


def edit_transaction(trans_id):
    '''Handler for editing a transaction record'''
    # Check if transaction id is valid
    cur = db.cursor()
    if cur.execute(
            'SELECT COUNT(*) FROM transactions WHERE trans_id = {}'.format(trans_id)
    ).fetchone()[0] == 0:
        print('No transaction was found with ID `{}`'.format(trans_id))
        return

    # Get the current transaction record
    transaction = cur.execute('SELECT description, credit, amount, budget_category FROM \
        transactions WHERE trans_id = {}'.format(trans_id)).fetchone()

    # Get and validate user input
    desc = input('New description ({}...): '.format(transaction[0][:6]))
    if len(desc) <= 0:
        desc = None

    credit = input('Credit (withdrawal) or Debit (deposit)? (C/D): ')
    if len(credit) <= 0:
        credit = None
    elif credit.lower() == 'c':
        credit = 1
    elif credit.lower() == 'd':
        credit = 0
    else:
        print('Incorrect entry for credit/debit.')
        return

    amount = input('Transaction amount (${}): '.format(transaction[2]))
    if len(amount) <= 0:
        amount = None
    else:
        amount = float(re.sub(r'[^0-9\.]', '', amount))

    category = input('Budget category ({}): '.format(transaction[3]))
    if category.lower() in ('', 'none', 'null', 'n/a'):
        category = None
    else:
        cur.execute('SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}"'.format(category))
        if cur.fetchone()[0] == 0:
            print('No budget category was found under the name `{}`'.format(category))
            return

    # Call the helper function
    success = _edit_transaction(trans_id, desc, credit, amount, category)
    if success:
        db.commit()
        print('Transaction updated')
        return

    print('Failed to update transaction.')
    return
