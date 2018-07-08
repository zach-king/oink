"""
File: transactions.py
"""

from __future__ import print_function
import re
from datetime import datetime
import locale

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db, accounts, budget, category, utils
from .colorize import color_error, color_info, color_input, color_success, colorize_headers, colorize, colorize_list


DEPOSIT_ID = 0
WITHDRAWAL_ID = 1


class TransactionType(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Transaction(object):
    def __init__(self, id, account_id, transaction_type_id, transaction_type_name, description, amount, category_id, category_name, created_at):
        self.id = id
        self.account_id = account_id
        self.transaction_type = TransactionType(transaction_type_id, transaction_type_name)
        self.description = description
        self.amount = amount
        self.category = category.Category(category_id, category_name)
        self.created_at = created_at


def list_for_account(account_id, from_date='0000-00-00', to_date='9999-99-99'):
    cur = db.cursor()
    transacts = cur.execute('SELECT t.id, t.account_id, tt.id, tt.name, t.description, t.amount, c.id, c.name, t.created_at \
        FROM transactions t \
        LEFT JOIN transaction_types tt ON t.transaction_type_id = tt.id \
        LEFT JOIN categories c ON t.category_id = c.id \
        WHERE t.account_id = ? AND t.created_at BETWEEN ? AND ? \
        ORDER BY t.created_at', (account_id, from_date, to_date,)).fetchall()
    trans = [Transaction(*row) for row in transacts]
    return trans


def setup():
    """
    Initial database setup; creates the `transactions` table
    """
    global WITHDRAWAL_ID, DEPOSIT_ID

    locale.setlocale(locale.LC_ALL, '')
    cur = db.cursor()

    # Create transaction_types table
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS transaction_types (
            id integer PRIMARY KEY AUTOINCREMENT,
            name text NOT NULL,
            UNIQUE(name)
        );
        '''
    )
    db.commit()

    # Insert the default transaction types
    cur.execute(f'''
        INSERT INTO transaction_types (id, name)
        SELECT {DEPOSIT_ID}, 'deposit'
        WHERE NOT EXISTS(SELECT 1 FROM transaction_types WHERE id = {DEPOSIT_ID} AND name = 'deposit');
        ''')
    cur.execute(f'''
        INSERT INTO transaction_types (id, name)
        SELECT {WITHDRAWAL_ID}, 'withdrawal'
        WHERE NOT EXISTS(SELECT 1 FROM transaction_types WHERE id = {WITHDRAWAL_ID} AND name = 'withdrawal');
        ''')
    db.commit()

    # Create transactions table
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS transactions (
            id integer PRIMARY KEY AUTOINCREMENT,
            account_id integer NOT NULL,
            transaction_type_id integer NOT NULL,
            description text,
            amount integer NOT NULL,
            category_id integer,
            created_at text NOT NULL,
            FOREIGN KEY (account_id)
                REFERENCES accounts (id)
                ON UPDATE CASCADE
                ON DELETE NO ACTION,
            FOREIGN KEY (transaction_type_id)
                REFERENCES transaction_types (id)
                ON UPDATE CASCADE
                ON DELETE NO ACTION,
            FOREIGN KEY (category_id)
                REFERENCES categories (id)
                ON UPDATE CASCADE
                ON DELETE NO ACTION
        );
        ''')
    db.commit()

def create(account_id, description, type_id, amount, category_id=None):
    """
    Helper function for adding a transaction
    """
    cur = db.cursor()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert the transaction record
    cur.execute('INSERT INTO transactions (account_id, transaction_type_id, description, amount, category_id, created_at) \
        VALUES (?, ?, ?, ?, ?, ?)', (account_id, type_id, description, amount, category_id, created_at))

    if cur.rowcount == 0:
        print(color_error('[error]') + ' Failed to record transaction.')
        return

    # Now withdraw or deposit from the account as recorded
    prev_balance = accounts.get_balance(account_id)
    new_balance = 0
    if type_id == WITHDRAWAL_ID:
        new_balance = prev_balance - amount
    elif type_id == DEPOSIT_ID:
        new_balance = prev_balance + amount
    else:
        print(color_warning(f'Unexpected transaction type "{type_id}" received. Account balance will not be affected.'))
        return True

    # Set the new balance
    success = accounts.set_balance(account_id, new_balance)

    return success


def list_transaction_types():
    """
    Prints out the available transaction types
    """
    types = db.cursor().execute('SELECT id, name FROM transaction_types ORDER BY id').fetchall()
    headers = colorize_headers(['ID', 'Name'])
    print(tabulate(types, headers=headers, tablefmt='psql'))


def type_exists(type_id):
    """
    Whether or not a type by `type_id` exists
    """
    return db.cursor().execute('SELECT COUNT(*) FROM transaction_types WHERE id = ?', (type_id,)).fetchone()[0] != 0


def new():
    """
    Handler to record a new transaction in a given account
    """
    while True:
        account_id = input(color_input('Account ID: '))

        if len(account_id) <= 0:
            print(color_info('Record transaction cancelled.'))
            return

        account_id = int(account_id)
        cur = db.cursor()

        if not accounts.exists(int(account_id)):
            print(color_error('[error]') + ' No account was found with ID `{}`.'.format(account_id))
            continue

        description = input(color_input('Transaction description: '))
        if len(description) <= 0:
            print(color_info('Record transaction cancelled.'))
            return

        print('')
        list_transaction_types()  # Prints out available transaction types
        _type = input(color_input('\nSelect a transaction type (ID): '))
        if len(_type) <= 0:
            print(color_info('Record transaction cancelled.'))
            return
        _type = int(_type)
        if not type_exists(_type):
            print(color_error('[error]') + ' Invalid type ID selected.')
            continue

        amount = input(color_input('Transaction amount: '))
        if len(amount) <= 0:
            print(color_info('Record transaction cancelled.'))
            return
        amount = float(re.sub(r'[^0-9\.]', '', amount))

        print('')
        category.print_list()  # Prints out available categories
        category_id = input(color_input('Category ID: '))
        if category_id.lower() in ('', 'none', 'null', 'n/a'):
            category_id = None
        else:
            category_id = int(category_id)
            if not category.get(category_id):
                print(color_error('[error]') + ' No category was found under the ID `{}`'.format(category_id))
                continue

        # Call the helper function
        success = create(account_id, description, _type, utils.float_to_atomic(amount), category_id)
        if success:
            db.commit()
            print(color_success('Transaction recorded'))
            return

        print(color_error('[error]') + ' Failed to update balance.')
        return

def list_all_transactions(num=10):
    """
    Handler to list transactions for all accounts
    """
    if num in (None, '*'):
        num = -1

    cur = db.cursor()
    cur.execute(
        'SELECT transactions.id, account.name, transactions.description, type.id, type.name, transactions.amount, \
        category.name, transactions.created_at FROM transactions \
        LEFT JOIN accounts account ON transactions.account_id = account.id \
        LEFT JOIN transaction_types type ON transactions.transaction_type_id = type.id \
        LEFT JOIN categories category ON transactions.category_id = category.id \
        ORDER BY transactions.created_at DESC, transactions.id DESC \
        LIMIT ?', (num,))
    rows = cur.fetchall()

    # Place (+/-) in front of amount in response to credit/debit
    new_rows = []
    for row in rows:
        amount = utils.atomic_to_float(row[5])
        str_amount = ''
        if row[3] == WITHDRAWAL_ID: # Credit
            str_amount = colorize('-' + locale.currency(amount, grouping=True), 'red')
        elif row[3] == DEPOSIT_ID:
            str_amount = colorize('+' + locale.currency(amount, grouping=True), 'green')
        else:
            str_amount = colorize(' ' + locale.currency(amount, grouping=True), 'yellow')
        new_rows.append(colorize_list(row[:3], ['white', 'cyan', 'yellow']) + [colorize(row[4], 'white'), str_amount,] + colorize_list(row[6:], ['purple', 'white']))

    headers = colorize_headers([
        'ID', 'Account', 'Description', 'Type',
        'Amount', 'Category', 'Created At'])
    print(tabulate(new_rows, headers=headers, tablefmt='psql'))

def list_transactions(account_id=None, num=10):
    """
    Handler to list transactions for a given account.
    """
    if account_id in (None, '*'):
        list_all_transactions(num)
        return
    account_id = int(account_id)

    if num in (None, '*'):
        num = -1

    cur = db.cursor()

    if not accounts.exists(account_id):
        print(color_error('[error]') + ' No account was found by the ID `{}`'.format(acct))
        return

    cur.execute(
        'SELECT transactions.id, account.name, transactions.description, type.id, type.name, transactions.amount, \
        category.name, transactions.created_at FROM transactions \
        LEFT JOIN accounts account ON transactions.account_id = account.id \
        LEFT JOIN transaction_types type ON transactions.transaction_type_id = type.id \
        LEFT JOIN categories category ON transactions.category_id = category.id \
        WHERE transactions.account_id = ? \
        ORDER BY transactions.created_at DESC, transactions.id DESC \
        LIMIT ?', (account_id, num,))
    rows = cur.fetchall()

    # Place (+/-) in front of amount in response to credit/debit
    new_rows = []
    for row in rows:
        amount = utils.atomic_to_float(row[5])
        str_amount = ''
        if row[3] == WITHDRAWAL_ID: # Credit
            str_amount = colorize('-' + locale.currency(amount, grouping=True), 'red')
        elif row[3] == DEPOSIT_ID:
            str_amount = colorize('+' + locale.currency(amount, grouping=True), 'green')
        else:
            str_amount = colorize(' ' + locale.currency(amount, grouping=True), 'yellow')
        new_rows.append(colorize_list(row[:3], ['white', 'cyan', 'yellow']) + [colorize(row[4], 'white'), str_amount,] + colorize_list(row[6:], ['purple', 'white']))

    headers = colorize_headers([
        'ID', 'Account', 'Description', 'Type',
        'Amount', 'Category', 'Created At'])
    print(tabulate(new_rows, headers=headers, tablefmt='psql'))


def add_transfer(amount, source_acct_id, dest_acct_id):
    """
    Handler for adding a transfer transaction between two accounts
    """
    # Check for optargs and validate data
    cur = db.cursor()
    source_acct_id = int(source_acct_id)
    dest_acct_id = int(dest_acct_id)
    accts = [acct[0] for acct in cur.execute('SELECT id FROM accounts')]
    if source_acct_id in (None, ''):
        print(color_info('Transfer transaction cancelled.'))
        return
    if source_acct_id not in accts:
        print(color_error('[error]') + ' The source account (ID: {}) does not exist.'.format(source_acct_id))
        return

    if dest_acct_id in (None, ''):
        print(color_info('Transfer transaction cancelled.'))
        return
    if dest_acct_id not in accts:
        print(color_error('[error]') + ' The destination account (ID: {}) does not exist.'.format(dest_acct_id))
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

    amount = utils.float_to_atomic(amount)

    # Make the two transactions on the accounts
    success = create(source_acct_id, 'Transfer to Account ID {}'.format(dest_acct_id), WITHDRAWAL_ID, amount, None)
    success = success and create(dest_acct_id, 'Transfer from Account ID {}'.format(source_acct_id), DEPOSIT_ID, amount, None)

    if success:
        print(color_success('Transfer from account {} to {} recorded.'.format(source_acct_id, dest_acct_id)))
        db.commit()
        return

    print(color_error('[error]') + ' Failed to record transfer transaction from account {} to {}.'.format(source_acct_id, dest_acct_id))


def delete_transaction(trans_id):
    """
    Handler for the delete a transaction command
    """
    # Validate the transaction id
    cur = db.cursor()
    if trans_id in (None, ''):
        print(color_info('Delete transaction cancelled.'))
        return

    try:
        trans_id = int(trans_id)
    except ValueError:
        print(color_error('[error]') + ' Transaction ID must be an integer!')
        return

    exists = cur.execute('SELECT COUNT(*) FROM transactions WHERE id = ?', (trans_id,)).fetchone()[0] == 1
    if not exists:
        print(color_error('[error]') + ' No transaction was found with ID `{}`'.format(trans_id))
        return

    # Counter the transaction effect
    transaction = cur.execute('SELECT account_id, transaction_type_id, amount FROM transactions \
        WHERE id = ?', (trans_id,)).fetchone()
    account_id = transaction[0]
    type_id = transaction[1]
    amount = transaction[2]
    if type_id == DEPOSIT_ID:
        amount *= -1

    # Update the balance of the account
    accounts.set_balance(account_id, accounts.get_balance(account_id) + amount)

    # Valid and exists so delete
    cur.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
    if cur.execute('SELECT COUNT(*) FROM transactions WHERE id = ?', (trans_id,)).fetchone()[0] != 0:
        print(color_error('[error]') + ' Failed to delete transaction.')
        return

    print(color_success('Transaction deleted.'))
    db.commit()


def _edit_transaction(trans_id, description=None, type_id=None, amount=None, category_id=None):
    """
    Helper function for updating a transaction record
    """
    cur = db.cursor()
    # Get current record
    transaction = cur.execute('SELECT description, transaction_type_id, amount, category_id FROM \
        transactions WHERE id = ?', (trans_id,)).fetchone()

    if cur.rowcount == 0:
        print(color_error('[error]') + ' Transaction not found.')
        return False

    if description is None:
        description = transaction[0]
    if type_id is None:
        type_id = transaction[1]
    if not amount and amount != 0:
        amount = transaction[2]
    if category_id is None:
        category_id = transaction[3]

    # Update where different
    cur.execute('UPDATE transactions SET description = ?, transaction_type_id = ?, \
        amount = ?, category_id = ? WHERE id = ?', (
            description, type_id, amount, category_id, trans_id,
        ))

    if cur.rowcount != 1:
        return False

    # Check for change of credit in case need balance update
    success = True
    acct_id = cur.execute('SELECT account_id FROM transactions WHERE id = ?', (trans_id,)).fetchone()[0]
    if transaction[1] == WITHDRAWAL_ID:
        # Add the money back
        success = accounts.set_balance(acct_id, accounts.get_balance(acct_id) + transaction[2])
    elif transaction[1] == DEPOSIT_ID:
        success = accounts.set_balance(acct_id, accounts.get_balance(acct_id) - transaction[2])

    # Apply new transaction effect
    if type_id == WITHDRAWAL_ID:
        # Need to subtract the amount from the account
        success &= accounts.set_balance(acct_id, accounts.get_balance(acct_id) - amount)
    elif type_id == DEPOSIT_ID:
        # Need to add the amount to the account
        success &= accounts.set_balance(acct_id, accounts.get_balance(acct_id) + amount)

    if success:
        db.commit()
        return True
    return False


def edit_transaction(trans_id):
    """
    Handler for editing a transaction record
    """
    # Check if transaction id is valid
    trans_id = int(trans_id)
    cur = db.cursor()
    if cur.execute(
            'SELECT COUNT(*) FROM transactions WHERE id = ?', (trans_id,)
    ).fetchone()[0] == 0:
        print('No transaction was found with ID `{}`'.format(trans_id))
        return

    # Get the current transaction record
    transaction = cur.execute('SELECT description, transaction_type_id, amount, category_id FROM \
        transactions WHERE id = ?', (trans_id,)).fetchone()

    # Get and validate user input
    desc = input(color_input('New description ({}...): '.format(transaction[0][:6])))
    if len(desc) <= 0:
        desc = None

    print('')
    list_transaction_types()
    type_id = input(color_input('\nSelect a Transaction Type (ID): '))
    if len(type_id) <= 0:
        print(color_info('Record transaction cancelled.'))
        return
    type_id = int(type_id)
    if not type_exists(type_id):
        print(color_error('[error]') + ' Invalid type ID selected.')
        return

    amount = input(color_input('Transaction amount (${}): '.format(utils.atomic_to_float(transaction[2]))))
    if len(amount) <= 0:
        amount = None
    else:
        amount = float(re.sub(r'[^0-9\.]', '', amount))

    print('')
    category.print_list()  # Prints out available categories
    category_id = input(color_input('Category ID: '))
    if category_id.lower() in ('', 'none', 'null', 'n/a'):
        category_id = None
    else:
        category_id = int(category_id)
        if not category.get(category_id):
            print(color_error('[error]') + ' No category was found under the ID `{}`'.format(category_id))
            return

    # Call the helper function
    success = _edit_transaction(trans_id, desc, type_id, utils.float_to_atomic(amount) if amount else None, category_id)
    if success:
        db.commit()
        print(color_success('Transaction updated'))
        return

    print(color_error('[error]') + ' Failed to update transaction.')
    return
