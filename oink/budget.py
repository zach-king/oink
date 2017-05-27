'''
File: budget.py
'''

from __future__ import print_function
import datetime

from tabulate import tabulate

from . import db


def setup():
    '''
    Setup budgeting table(s).
    '''
    budget_categories_sql = '''
    CREATE TABLE IF NOT EXISTS budget_categories (
        category_name text PRIMARY KEY,
        budget_amount integer NOT NULL,
        budget_acct text NOT NULL,
        FOREIGN_KEY budget_acct
            REFERENCES accounts (name)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    '''
    cur = db.cursor()
    cur.execute(budget_categories_sql)
    db.commit()


def create_budget():
    '''Handler for creating a new budget'''
    # Get the budget category inputs from user
    budget_name = input('Budget category name: ')

    # Data validation
    if budget_name == '' or budget_name is None:
        print('Invalid budget category name `{}`.'.format(budget_name))
        return False

    budget_amount = input('Budget amount: ')
    try:
        budget_amount = float(budget_amount)
    except ValueError:
        print('Invalid budget amount specified. Amount must be a numeric value.')
        return False

    if budget_amount < 0 or budget_amount is None:
        print('Invalid budget amount specified. Amount must not be less than zero.')
        return False

    acct_name = input('Account name: ')
    if acct_name == '' or acct_name is None:
        print('Invalid account name `{}` for budget assignment.'.format(acct_name))
        return False

    # Create the budget
    _create_budget(budget_name, budget_amount, acct_name)


def _create_budget(name, amount, acct):
    '''Private function delegated to creating new budgets'''
    # Validate arguments
    if name == '' or name is None:
        print('Invalid budget category name `{}`.'.format(str(name)))
        return False
    if amount < 0 or amount is None:
        print('Invalid budget amount specified. Amount must not be less than zero.')
        return False
    if acct == '' or acct is None:
        print('Invalid account name `{}` for budget assignment.'.format(str(acct)))
        return False

    # Check if the budget name already exists
    cur = db.cursor()
    budget_exists = cur.execute(
        'SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}"'.format(name)
    ).fetchone()[0]

    if budget_exists:
        print('A budget category already exists under the name `{}`.'.format(str(name)))
        return False

    # Check if the account tied to this budget exists
    acct_exists = cur.execute(
        'SELECT COUNT(*) FROM accounts WHERE name = "{}"'.format(acct)
    ).fetchone()[0]

    if not acct_exists:
        print('No account was found under the name `{}`.'.format(str(acct)))
        return False

    # ALl checks have passed; create the budget category
    cur.execute(
        'INSERT INTO budget_categories(category_name, budget_amount, budget_acct) \
        VALUES (?, ?, ?)', (name, amount, acct)
    )

    # Check that the insertion completed successfully
    success = cur.execute(
        'SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}"'.format(name)
    ).fetchone()[0]

    if success:
        db.commit()
        print('New budget category `{}` created successfully.'.format(name))
        return True

    print('Failed to create new budget category `{}`.'.format(name))
    return False


def list_all_budgets():
    '''Handler for listing all budget data'''
    cur = db.cursor()
    cur.execute('SELECT category_name, budget_amount, budget_acct \
        FROM budget_categories ORDER BY budget_acct DESC')
    rows = cur.fetchall()

    print(tabulate(rows, headers=['Category', 'Budget', 'Account'], \
        tablefmt='psql'))


def list_budget(month=None, year=None):
    '''Handler for listing budget data for all account for a month'''
    # Default month and year to current
    if month is None:
        month = str(datetime.datetime.today().month)
    if year is None:
        year = str(datetime.datetime.today().year)

    # Data validation
    if not str(month).isdecimal() or (int(month) < 1 or int(month) > 12):
        print('Invalid value for <month>. Month should be a number 1-12.')
        return
    elif int(month) > datetime.datetime.today().month:
        print('Cannot list budget data for the future :O')
        return

    if not str(year).isdecimal() or \
        (int(year) > datetime.datetime.today().year) or \
        len(str(year)) != 4:
        print('Invalid value for year. Year must be a four-digit integer, ' + \
        'and cannot be in the future!')
        return

    if len(str(month)) == 1:
        month = '0' + month

    # Loop through budgets, and for the account that is attached to it
    # loop through its transactions, matching the budget category;
    # then evaluate the budget result (overbudget or underbudget)
    budget_cur = db.cursor()
    trans_cur = db.cursor()
    rows = []
    for budget in budget_cur.execute('SELECT category_name, budget_amount, budget_acct \
        FROM budget_categories'):
        result = budget[1] # Budget amount
        transaction_query = 'SELECT credit, amount FROM transactions WHERE acct = "{}" AND budget_category = "{}" AND recorded_on LIKE "{}"'
        transaction_query = transaction_query.format(budget[2],  budget[0], str(year) + '-' + str(month) + '%')
        for transaction in trans_cur.execute(transaction_query):
            if transaction[0] == 1:
                result -= transaction[1]
        rows.append([budget[0], budget[2], budget[1], result])

    print(tabulate(rows, headers=['Category', 'Account', 'Budget', 'Balance'], \
        tablefmt='psql'))

