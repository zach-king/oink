'''
File: budget.py
'''

from __future__ import print_function
import datetime

from tabulate import tabulate

from . import db
from .colorize import colorize, reset


def setup():
    '''
    Setup budgeting table(s).
    '''
    budget_categories_sql = '''
    CREATE TABLE IF NOT EXISTS budget_categories (
        category_name text,
        budget_amount integer NOT NULL,
		budget_acct text NOT NULL,
        month text NOT NULL,
        FOREIGN KEY (budget_acct)
            REFERENCES accounts (name)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
        PRIMARY KEY (category_name, month)
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
        return

    budget_amount = input('Budget amount: ')
    try:
        budget_amount = float(budget_amount)
    except ValueError:
        print('Invalid budget amount specified. Amount must be a numeric value.')
        return

    if budget_amount < 0 or budget_amount is None:
        print('Invalid budget amount specified. Amount must not be less than zero.')
        return

    acct_name = input('Account name: ')
    if acct_name == '' or acct_name is None:
        print('Invalid account name `{}` for budget assignment.'.format(acct_name))
        return

    # Create the budget
    _create_budget(budget_name, budget_amount, acct_name)


def _create_budget(name, amount, acct):
    '''Private function delegated to creating new budgets'''
    # Validate arguments
    if name == '' or name is None:
        print('Invalid budget category name `{}`.'.format(str(name)))
        return False
    if float(amount) < 0 or amount is None:
        print('Invalid budget amount specified. Amount must not be less than zero.')
        return False
    if acct == '' or acct is None:
        print('Invalid account name `{}` for budget assignment.'.format(str(acct)))
        return False

    # Check if the budget name already exists
    cur = db.cursor()
    month = datetime.datetime.now().strftime('%Y-%m')
    budget_exists = cur.execute(
        'SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}" \
        AND month = "{}"'.format(name, month)
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
        'INSERT INTO budget_categories(category_name, budget_amount, budget_acct, month) \
        VALUES (?, ?, ?, ?)', (name, amount, acct, month)
    )

    # Check that the insertion completed successfully
    success = cur.execute(
        'SELECT COUNT(*) FROM budget_categories WHERE \
        category_name = "{}" AND month = "{}"'.format(name, month)
    ).fetchone()[0]

    if success:
        db.commit()
        return True

    print('Failed to create new budget category `{}`.'.format(name))
    return False


def list_all_budgets(month=None):
    '''Handler for listing all budget data'''
    cur = db.cursor()
    if month is None:
        month = datetime.datetime.now().strftime('%Y-%m')

    exists = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE \
        month = "{}"'.format(month)).fetchone()[0]
    if exists == 0:
        print('No budgets were found for the month of `{}`'.format(month))
        return

    cur.execute('SELECT category_name, budget_amount, budget_acct \
        FROM budget_categories WHERE month = "{}" ORDER BY budget_acct DESC'.format(month))
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
        month = '0' + str(month)
    budget_month = str(year) + '-' + str(month)

    # Loop through budgets, and for the account that is attached to it
    # loop through its transactions, matching the budget category;
    # then evaluate the budget result (overbudget or underbudget)
    budget_cur = db.cursor()
    trans_cur = db.cursor()
    rows = []
    for budget in budget_cur.execute('SELECT category_name, budget_amount, budget_acct \
        FROM budget_categories WHERE month = "{}"'.format(budget_month)):
        result = budget[1] # Budget amount
        transaction_query = 'SELECT credit, amount FROM transactions WHERE acct = "{}" AND budget_category = "{}" AND recorded_on LIKE "{}"'
        transaction_query = transaction_query.format(budget[2],  budget[0], str(year) + '-' + str(month) + '%')
        for transaction in trans_cur.execute(transaction_query):
            if transaction[0] == 1:
                result -= transaction[1]
        if result > 0: # Good; means budget has not run out
            result = colorize('+' + str(result), 'green')
        else:
            result = colorize(str(reset), 'red')
        rows.append([budget[0], budget[2], budget[1], result])

    print(tabulate(rows, headers=['Category', 'Account', 'Budget', 'Balance'], \
        tablefmt='psql'))


def set_budget(category, amount):
    '''Handler for set budget command'''
    cur = db.cursor()
    # Check if category exists
    exists = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}"'.format(
        category)).fetchone()[0]
    if exists == 0:
        print('No budget category found named `{}`'.format(category))
        return

    # Check if the budget exists for the *current* month
    month = datetime.datetime.now().strftime('%Y-%m')
    exists = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE \
        category_name = "{}" AND month = "{}"'.format(category, month)).fetchone()[0]

    # Validate amount
    if float(amount) < 0:
        print('Budget amount cannot be less than zero.')
        return

    # If the current month does not exist, create it
    if not exists:
        acct = cur.execute('SELECT budget_acct FROM budget_categories \
            WHERE category_name = "{}"'.format(category)).fetchone()[0]
        if not _create_budget(category, amount, acct):
            print('Unable to create new budget for the month of `{}`'.format(month))
            return

    # Update the budget
    cur.execute('UPDATE budget_categories SET budget_amount = {} WHERE \
    category_name = "{}" AND month = "{}"'.format(
        amount, category, month))

    if cur.rowcount != 1:
        print('Failed to set the budget for `{}`'.format(category))
        return

    print('Budget set for category `{}` for the month of `{}`'.format(category, month))
    db.commit()


def rename_budget(category, new_name):
    '''Handler for renaming a budget category'''
    cur = db.cursor()

    # Check if category exists in db
    exists = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE \
        category_name = "{}"'.format(category)).fetchone()[0]
    if not exists:
        print('Budget category `{}` does not exist.'.format(category))
        return

    # Check if a category already exists with new_name
    exists = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE \
        category_name = "{}"'.format(new_name)).fetchone()[0]
    if exists:
        print('Budget category `{}` already exists.'.format(new_name))
        return

    # Rename the category
    cur.execute('UPDATE budget_categories SET category_name = "{}" \
        WHERE category_name = "{}"'.format(new_name, category))

    # Check for success
    success = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE \
        category_name = "{}"'.format(new_name)).fetchone()[0]
    if not success:
        print('Failed to rename the budget category `{}`'.format(category))
        return
    print('Budget category `{}` renamed to `{}`'.format(category, new_name))
    db.commit()


def _delete_budget(category):
    '''Helper function for deleting a budget category'''
    cur = db.cursor()
    month = datetime.datetime.now().strftime('%Y-%m')

    # Check if category exists in db
    exists = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE \
        category_name = "{}" AND month = "{}"'.format(category, month)).fetchone()[0]
    if not exists:
        print('Budget category `{}` does not exist.'.format(category))
        return False

    # Try to delete the budget category
    cur.execute('DELETE FROM budget_categories WHERE \
        category_name = "{}" AND month = "{}"'.format(category, month))

    # Check for success
    failure = cur.execute('SELECT COUNT(*) FROM budget_categories WHERE \
        category_name = "{}" AND month = "{}"'.format(category, month)).fetchone()[0]

    return not failure


def delete_budget(category):
    '''Handler for deleting a budget category'''
    success = _delete_budget(category)
    month = datetime.datetime.now().strftime('%Y-%m')
    if not success:
        print('Failed to delete budget category `{}`'.format(category))
    else:
        print('Budget category `{}` deleted for the month `{}`.'.
              format(category, month))
        db.commit()
