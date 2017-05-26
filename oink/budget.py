'''
File: budget.py
'''

from __future__ import print_function

from . import db


def setup():
    '''
    Setup budgeting table(s).
    '''
    budget_categories_sql = '''
    CREATE TABLE IF NOT EXISTS budget_categories (
        category_name text NOT NULL PRIMARY KEY,
        budget_amount integer NOT NULL,
        budget_acct text NOT NULL,
        FOREIGN_KEY (budget_acct) 
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
    budget_amount = input('Budget amount: ')
    acct_name = input('Account name: ')
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
        'SELECT COUNT(*) FROM budget_categories WHERE category_name = "{}".'.format(name)
    ).fetchone()[0]

    if budget_exists:
        print('A budget category already exists under the name `{}`.'.format(str(name)))
        return False

    # Check if the account tied to this budget exists
    acct_exists = cur.execute(
        'SELECT COUNT(*) FROM accounts WHERE name = "{}".'.format(acct)
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
        print('New budget category `{}` created successfully.'.format(name))
        return True

    print('Failed to create new budget category `{}`.'.format(name))
    return False


