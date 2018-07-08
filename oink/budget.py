"""
File: budget.py
"""

from __future__ import print_function
import datetime
import locale

from tabulate import tabulate

from . import db, utils, category, accounts, transactions
from .colorize import color_error, color_info, color_input, color_success, colorize_headers, colorize, colorize_list


class Budget(object):
    def __init__(self, id, account_id, category_id, category_name, amount, year, month, created_at):
        self.id = id
        self.account_id = account_id
        self.category = category.Category(category_id, category_name)
        self.amount = amount
        self.year = year
        self.month = month
        self.created_at = created_at
        self.balance = get_balance(self)


def list_for_account(account_id, from_date='0000-00-00', to_date='9999-99-99'):
    # Parse months and years from arguments
    from_date = from_date.split('-')
    if len(from_date) > 1:
        from_year, from_month = [int(x) for x in from_date[:2]]
    else:
        from_year = int(from_date[0])
        from_month = 0
    to_date = to_date.split('-')
    if len(to_date) > 1:
        to_year, to_month = [int(x) for x in to_date[:2]]
    else:
        to_year = int(to_date[0])
        to_month = 12

    cur = db.cursor()
    buds = cur.execute('SELECT b.id, b.account_id, c.id, c.name, b.amount, b.year, b.month, b.created_at \
        FROM budgets b \
        LEFT JOIN categories c ON b.category_id = c.id \
        WHERE b.account_id = ? AND b.year BETWEEN ? AND ? \
        AND b.month BETWEEN ? AND ? \
        ORDER BY b.year, b.month', (account_id, from_year, to_year, from_month, to_month,)).fetchall()
    return [Budget(*row) for row in buds]


def get_balance(budget):
    transaction_query = 'SELECT transaction_type_id, amount FROM transactions \
        WHERE account_id = ? AND category_id = ? AND created_at BETWEEN ? AND ?'
    month = budget.month
    year = budget.year
    next_month = month + 1
    t_month = '0' + str(month) if len(str(month)) == 1 else str(month)
    next_month = month + 1 if month < 12 else 1
    t_next_month = '0' + str(next_month) if len(str(next_month)) == 1 else str(next_month)
    t_year = str(year)
    t_next_year = t_year if next_month != 1 else str(year + 1)

    result = budget.amount
    trans = db.cursor().execute(transaction_query, (budget.account_id, budget.category.id, f'{t_year}-{t_month}', f'{t_next_year}-{t_next_month}'))
    for transaction in trans:
        type_id = transaction[0]
        amount = transaction[1]
        if type_id == transactions.WITHDRAWAL_ID:
            result -= amount
        elif type_id == transactions.DEPOSIT_ID:
            result += amount

    return result


def setup():
    """
    Setup budgeting table(s).
    """
    locale.setlocale(locale.LC_ALL, '')
    budgets_sql = '''
    CREATE TABLE IF NOT EXISTS budgets (
        id integer PRIMARY KEY AUTOINCREMENT,
        account_id integer NOT NULL,
        category_id integer NOT NULL,
        amount integer NOT NULL,
		created_at text NOT NULL,
        year integer NOT NULL,
        month integer NOT NULL,
        FOREIGN KEY (account_id)
            REFERENCES accounts (id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
        FOREIGN KEY (category_id)
            REFERENCES categories (id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
        UNIQUE(account_id, category_id, month, year)
    );
    '''

    cur = db.cursor()
    cur.execute(budgets_sql)
    db.commit()


def new(account_id):
    """
    Handler for creating a new budget
    """
    account_id = int(account_id)
    if not accounts.exists(account_id):
        print(color_error('[error]') + ' Account does not exist (ID: {})'.format(account_id))
        return

    # Get the budget category inputs from user
    category.print_list()
    category_id = input(color_input('\nSelect a category (ID) to budget: '))

    # Data validation
    if category_id in (None, ''):
        print(color_info('Budget creation cancelled.' ))
        return
    category_id = int(category_id)

    budget_amount = input(color_input('Budget amount: '))
    try:
        budget_amount = float(budget_amount)
    except ValueError:
        print(color_error('[error]') + ' Invalid budget amount specified. ' + \
            'Amount must be a numeric value.')
        return

    if budget_amount < 0 or budget_amount is None:
        print(color_error('[error]') + ' Invalid budget amount specified. ' + \
            'Amount must not be less than zero.')
        return

    default_year = datetime.datetime.now().year
    default_month = datetime.datetime.now().month
    year = input(color_input('Budget year ({}): '.format(default_year)))
    month = input(color_input('Budget month ({}): '.format(default_month)))
    year = default_year if not year else year
    month = default_month if not month else month

    budget_amount = utils.float_to_atomic(budget_amount)

    # Create the budget
    if create(account_id, category_id, budget_amount, year, month):
        print(color_success('Budget category created'))


def create(account_id, category_id, amount, year, month):
    """
    Private function delegated to creating new budgets
    """
    # Check if the budget already exists
    cur = db.cursor()
    budget_exists = cur.execute(
        'SELECT COUNT(*) FROM budgets WHERE account_id = ? AND category_id = ? \
        AND year = ? and month = ?', (account_id, category_id, year, month,)
    ).fetchone()[0] != 0

    if budget_exists:
        print(color_error('[error]') + ' A budget already ' + \
            'exists for that account, category, and time period.')
        return False

    # Check if the account tied to this budget exists
    if not accounts.exists(account_id):
        print(color_error('[error]') + ' No account was found by ' + \
            'the ID `{}`.'.format(account_id))
        return False

    # ALl checks have passed; create the budget category
    cur.execute(
        'INSERT INTO budgets (account_id, category_id, amount, year, month, created_at) \
        VALUES (?, ?, ?, ?, ?, ?)', (account_id, category_id, amount, year, month, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
    )

    # Check that the insertion completed successfully
    if cur.rowcount == 1:
        db.commit()
        return True

    print(color_error('[error]') + ' Failed to create new budget.')
    return False


def list_all_budgets(month=None, year=None):
    """
    Handler for listing all budget data
    """
    cur = db.cursor()
    month = datetime.datetime.now().month if month is None else month
    year = datetime.datetime.now().year if year is None else year

    exists = cur.execute('SELECT COUNT(*) FROM budgets WHERE \
        year = ? AND month = ?', (year, month,)).fetchone()[0] != 0
    if not exists:
        print('No budgets were found for the month of {}/{}'.format(month, year))
        return

    cur.execute('SELECT b.id, a.name, c.name, b.amount, b.month, b.year, b.created_at \
        FROM budgets b \
        LEFT JOIN accounts a ON b.account_id = a.id \
        LEFT JOIN categories c ON b.category_id = c.id \
        WHERE b.year = ? AND b.month = ? \
        ORDER BY b.account_id DESC', (year, month,))
    rows = cur.fetchall()

    new_rows = []
    for row in rows:
        budget_id = row[0]
        account = row[1]
        category = row[2]
        amount = utils.atomic_to_float(row[3])
        month, year, created_at = row[4:7]
        new_rows.append([budget_id, account, category, locale.currency(amount, grouping=True), month, year, created_at])

    headers = colorize_headers(['ID', 'Account', 'Cateogory', 'Amount', 'Month', 'Year', 'Created At'])
    print(tabulate(new_rows, headers=headers, tablefmt='psql'))


def list_budget(month=None, year=None):
    """
    Handler for listing budget data for all accounts for a month
    """
    # Default month and year to current
    month = datetime.datetime.now().month if month is None else month
    year = datetime.datetime.now().year if year is None else year

    # Data validation
    if not str(month).isdecimal() or (int(month) < 1 or int(month) > 12):
        print(color_error('[error]') + ' Invalid value for <month>. Month should be a number 1-12.')
        return

    if not str(year).isdecimal() or \
        len(str(year)) != 4:
        print(color_error('[error]') + ' Invalid value for year. Year must be a ' + \
            'four-digit integer!')
        return

    month = int(month)
    year = int(year)

    # Loop through budgets, and for the account that is attached to it
    # loop through its transactions, matching the budget category;
    # then evaluate the budget result (overbudget or underbudget)
    budget_cur = db.cursor()
    trans_cur = db.cursor()
    rows = []
    for budget in budget_cur.execute('SELECT c.id, c.name, b.amount, a.id, a.name, b.created_at, b.id \
        FROM budgets b \
        LEFT JOIN accounts a ON b.account_id = a.id \
        LEFT JOIN categories c ON b.category_id = c.id \
        WHERE b.year = ? AND b.month = ?', (year, month,)):

        category_id = budget[0]
        category = budget[1]
        result = budget[2] # Budget amount
        budget_amount = utils.atomic_to_float(budget[2])
        account_id = budget[3]
        account = budget[4]
        created_at = budget[5]
        budget_id = budget[6]

        transaction_query = 'SELECT transaction_type_id, amount FROM transactions \
            WHERE account_id = ? AND category_id = ? AND created_at BETWEEN ? AND ?'
        next_month = month + 1
        t_month = '0' + str(month) if len(str(month)) == 1 else str(month)
        next_month = month + 1 if month < 12 else 1
        t_next_month = '0' + str(next_month) if len(str(next_month)) == 1 else str(next_month)
        t_year = str(year)
        t_next_year = t_year if next_month != 1 else str(year + 1)

        trans = trans_cur.execute(transaction_query, (account_id, category_id, f'{t_year}-{t_month}', f'{t_next_year}-{t_next_month}'))
        for transaction in trans:
            type_id = transaction[0]
            amount = transaction[1]
            if type_id == transactions.WITHDRAWAL_ID:
                result -= amount
            elif type_id == transactions.DEPOSIT_ID:
                result += amount

        result = utils.atomic_to_float(result)
        if result > 0: # Good; means budget has not run out
            result = colorize('+' + locale.currency(result, grouping=True), 'green')
        else:
            result = colorize('-' + locale.currency(-1 * result, grouping=True), 'red')
        lyst = [budget_id, account, category, locale.currency(budget_amount, grouping=True), month, year, created_at]
        rows.append(colorize_list(lyst[:4], ['white', 'purple', 'cyan', 'white']) + [result,] + colorize_list(lyst[4:], ['yellow', 'yellow', 'white']))

    headers = colorize_headers(['ID', 'Account', 'Category', 'Budget', 'Balance', 'Month', 'Year', 'Created At'])
    print(tabulate(rows, headers=headers, tablefmt='psql'))


def _delete_budget(budget_id):
    """
    Helper function for deleting a budget category
    """
    assert(isinstance(budget_id, int))

    cur = db.cursor()

    # Check if category exists in db
    exists = cur.execute('SELECT COUNT(*) FROM budgets WHERE \
        id = ?', (budget_id,)).fetchone()[0] != 0
    if not exists:
        print(color_error('[error]') + ' Budget does not exist for ID {}'.format(budget_id))
        return False

    # Try to delete the budget
    cur.execute('DELETE FROM budgets WHERE \
        id = ?', (budget_id,))

    # Check for success
    return cur.rowcount != 0


def delete_budget(budget_id):
    """
    Handler for deleting a budget category
    """
    budget_id = int(budget_id)

    success = _delete_budget(budget_id)
    if success:
        print(color_success('Budget (ID: {}) deleted.'.format(budget_id)))
        db.commit()
