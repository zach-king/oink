'''
File: transactions.py
'''

from __future__ import print_function
import re
from datetime import datetime
import locale

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db, accounts, budget
from .colorize import color_error, color_info, color_input, color_success, colorize_headers, colorize, colorize_list


def setup():
    '''
    Initial database setup; creates the `transactions` table
    '''
    locale.setlocale(locale.LC_ALL, '')
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
            budget_month text,
            recorded_on text NOT NULL,
            FOREIGN KEY (acct)
                REFERENCES accounts (name)
                ON UPDATE CASCADE
                ON DELETE CASCADE,
            FOREIGN KEY (budget_category, budget_month)
                REFERENCES budget_categories (category_name, month)
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
        cur.execute('INSERT INTO transactions(acct, description, credit, amount, budget_category, recorded_on, budget_month) \
            VALUES ("{}", "{}", {}, {}, "{}", "{}", "{}")'.format(acct, desc, credit, amount, category, recorded_on, datetime.now().strftime('%Y-%m')))
    else:
        cur.execute('INSERT INTO transactions(acct, description, credit, amount, budget_category, recorded_on) \
            VALUES ("{}", "{}", {}, {}, NULL, "{}")'.format(acct, desc, credit, amount, recorded_on))

    if cur.rowcount == 0:
        print(color_error('[error]') + ' Failed to record transaction.')
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
        name = input(color_input('Account Name: '))

        if len(name) <= 0:
            print(color_info('Record transaction cancelled.'))
            return

        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM accounts WHERE name = ?', (name,))
        result = cur.fetchone()
        count = result[0]

        if count <= 0:
            print(color_error('[error]') + ' Sorry, no account was found under the name `{}`.'.format(name))
            continue

        description = input(color_input('Transaction description: '))
        if len(description) <= 0:
            print(color_info('Record transaction cancelled.'))
            return

        credit = input(color_input('Credit (withdrawal) or Debit (deposit)? (C/D): '))
        if len(credit) <= 0:
            print(color_info('Record transaction cancelled.'))
            return
        if credit.lower() == 'c':
            credit = 1
        elif credit.lower() == 'd':
            credit = 0
        else:
            print(color_error('[error]') + ' Incorrect entry for credit/debit.')
            continue

        amount = input(color_input('Transaction amount: '))
        if len(amount) <= 0:
            print(color_info('Record transaction cancelled.'))
            return
        amount = float(re.sub(r'[^0-9\.]', '', amount))

        category = input(color_input('Budget category: '))
        if category.lower() in ('', 'none', 'null', 'n/a'):
            category = 'NULL'
        else:
            cur.execute('SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}"'.format(category))
            if cur.fetchone()[0] == 0:
                print(color_error('[error]') + ' No budget category was found under the name `{}`'.format(category))
                continue

        # Call the helper function
        success = _add_transaction(name, description, credit, amount, category)
        if success:
            db.commit()
            print(color_success('Transaction recorded'))
            return

        print(color_error('[error]') + ' Failed to update balance.')
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
        budget_category, recorded_on FROM transactions ORDER BY recorded_on DESC, trans_id DESC \
        {}'.format(limit_inject))
    rows = cur.fetchall()

    # Place (+/-) in front of amount in response to credit/debit
    new_rows = []
    for row in rows:
        str_amount = ''
        if row[3] == 1: # Credit
            str_amount = colorize('-' + locale.currency(row[4], grouping=True), 'red')
        else:
            str_amount = colorize('+' + locale.currency(row[4], grouping=True), 'green')
        new_rows.append(colorize_list(row[:3], ['gray', 'cyan', 'yellow']) + [str_amount,] + colorize_list(row[5:], ['purple', 'yellow']))

    headers = colorize_headers([
        'Transaction #', 'Account', 'Description',
        'Amount', 'Category', 'Recorded On'])
    print(tabulate(new_rows, headers=headers, tablefmt='psql'))

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
        print(color_error('[error]') + ' No account was found by the name `{}`'.format(acct))
        return

    cur.execute(
        'SELECT trans_id, acct, description, credit, amount, budget_category, \
        recorded_on FROM transactions WHERE acct = "{}" ORDER BY recorded_on \
        DESC, trans_id DESC {}'.format(acct, limit_inject))
    rows = cur.fetchall()

    # Place (+/-) in front of amount in response to credit/debit
    new_rows = []
    for row in rows:
        str_amount = ''
        if row[3] == 1: # Credit
            str_amount = colorize('-' + locale.currency(row[4], grouping=True), 'red')
        else:
            str_amount = colorize('+' + locale.currency(row[4], grouping=True), 'green')
        new_rows.append(colorize_list(row[:3], ['gray', 'cyan', 'yellow']) + [str_amount,] + colorize_list(row[5:], ['purple', 'yellow']))

    headers = colorize_headers([
        'Transaction #', 'Account', 'Description',
        'Amount', 'Category', 'Recorded On'
    ])
    print(tabulate(new_rows, headers=headers, tablefmt='psql'))


def add_transfer(source_acct=None, dest_acct=None, amount=None):
    '''Handler for adding a transfer transaction between two accounts'''
    # Check for optargs and validate data
    cur = db.cursor()
    accts = [acct[0] for acct in cur.execute('SELECT name FROM accounts')]
    if source_acct is None:
        source_acct = input(color_input('Source account name: '))
    if source_acct == '':
        print(color_info('Transfer transaction cancelled.'))
        return
    if source_acct not in accts:
        print(color_error('[error]') + ' The source account `{}` does not exist.'.format(source_acct))
        return

    if dest_acct is None:
        dest_acct = input(color_input('Destination account name: '))
    if dest_acct == '':
        print(color_info('Transfer transaction cancelled.'))
        return
    if dest_acct not in accts:
        print(color_error('[error]') + ' The destination account `{}` does not exist.'.format(dest_acct))
        return

    if amount is None:
        amount = input(color_input('Amount to transfer: '))
    try:
        amount = float(amount)
    except ValueError:
        print(color_error('[error]') + ' The amount must be a number!')
        return
    else:
        if amount <= 0:
            print(color_error('[error]') + ' The amount must be greater than zero!')
            return

    # Make the two transactions on the accounts
    success = _add_transaction(source_acct, 'Transfer to `{}`'.format(dest_acct), 1, amount, None)
    success = success and _add_transaction(dest_acct, 'Transfer from `{}`'.format(source_acct), 0, amount, None)

    if success:
        print(color_success('Transfer from `{}` to `{}` recorded.'.format(source_acct, dest_acct)))
        db.commit()
        return

    print(color_error('[error]') + ' Failed to record transfer transaction from `{}` to `{}`.'.format(source_acct, dest_acct))


def delete_transaction(trans_id):
    '''Handler for the delete a transaction command'''
    # Validate the transaction id
    cur = db.cursor()
    if trans_id == '' or trans_id is None:
        print(color_info('Delete transaction cancelled.'))
        return

    try:
        trans_id = int(trans_id)
    except ValueError:
        print(color_error('[error]') + ' Transaction ID must be an integer!')
        return

    rows = cur.execute('SELECT COUNT(*) FROM transactions WHERE trans_id = {}'.format(trans_id)).fetchone()
    if rows[0] != 1:
        print(color_error('[error]') + ' No transaction was found with ID `{}`'.format(trans_id))
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
        print(color_error('[error]') + ' Failed to delete transaction.')
        return

    print(color_success('Transaction deleted.'))
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
    if budget_category is not None:
        cur.execute('UPDATE transactions SET description = "{}", credit = {}, \
            amount = {}, budget_category = "{}" WHERE trans_id = {}'.format(
                description, credit, amount, budget_category, trans_id
            ))
    else:
        cur.execute('UPDATE transactions SET description = "{}", credit = {}, \
            amount = {}, budget_category = NULL WHERE trans_id = {}'.format(
                description, credit, amount, trans_id))

    if cur.rowcount != 1:
        return False

    # Check for change of credit in case need balance update
    success = True
    if credit != transaction[1]:
        acct = cur.execute('SELECT acct FROM transactions WHERE trans_id = {}'.format(trans_id)).fetchone()[0]
        if str(credit) == '1':
            # Need to subtract the amount from the account
            success = accounts.set_balance(acct, accounts.get_balance(acct) - (transaction[2] + amount))
        elif str(credit) == '0':
            # Need to add the amount to the account
            success = accounts.set_balance(acct, accounts.get_balance(acct) + (transaction[2] + amount))
    elif amount != transaction[2]:
        acct = cur.execute('SELECT acct FROM transactions WHERE trans_id = {}'.format(trans_id)).fetchone()[0]
        if str(credit) == '1':
            # Need to subtract the amount from the account
            success = accounts.set_balance(acct, accounts.get_balance(acct) + transaction[2] - amount)
        elif str(credit) == '0':
            # Need to add the amount to the account
            success = accounts.set_balance(acct, accounts.get_balance(acct) - transaction[2] + amount)

    if success:
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
    desc = input(color_input('New description ({}...): '.format(transaction[0][:6])))
    if len(desc) <= 0:
        desc = None

    credit = input(color_input('Credit (withdrawal) or Debit (deposit)? (C/D): '))
    if len(credit) <= 0:
        credit = None
    elif credit.lower() == 'c':
        credit = 1
    elif credit.lower() == 'd':
        credit = 0
    else:
        print(color_error('[error]') + ' Incorrect entry for credit/debit.')
        return

    amount = input(color_input('Transaction amount (${}): '.format(transaction[2])))
    if len(amount) <= 0:
        amount = None
    else:
        amount = float(re.sub(r'[^0-9\.]', '', amount))

    category = input(color_input('Budget category ({}): '.format(transaction[3])))
    if category.lower() in ('', 'none', 'null', 'n/a'):
        category = None
    else:
        cur.execute('SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}"'.format(category))
        if cur.fetchone()[0] == 0:
            print(color_error('[error]') + ' No budget category was found under the name `{}`'.format(category))
            return

    # Call the helper function
    success = _edit_transaction(trans_id, desc, credit, amount, category)
    if success:
        db.commit()
        print(color_success('Transaction updated'))
        return

    print(color_error('[error]') + ' Failed to update transaction.')
    return
