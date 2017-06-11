#!/usr/bin/python3
'''
File: _txt.py
Author: Zachary King

Implements the .txt report generation for Oink
'''

import os
from datetime import datetime
import locale

from .. import accounts, transactions, budget, db, colorize

from tabulate import tabulate

REPORT_WIDTH = 100

def generate_text_report(acct_no, acct_name, filepath):
    '''Generates a .TXT budgeting report'''

    locale.setlocale(locale.LC_ALL, '')

    with open(filepath, 'w') as fout:
        # Write the header info (date & account info)
        fout.write('-' * REPORT_WIDTH + '\n\n')
        fout.write('OINK REPORT'.center(REPORT_WIDTH))
        fout.write('\n\n')
        fout.write(('Generated on ' + datetime.now().strftime('%Y-%m-%d') + ' for the month of ' + datetime.now().strftime('%Y-%m')).center(REPORT_WIDTH))
        fout.write('\n')
        fout.write('-' * REPORT_WIDTH + '\n\n')

        fout.write(('Account: ' + acct_name).center(REPORT_WIDTH))
        fout.write('\n')
        fout.write(('Account #' + str(acct_no)).center(REPORT_WIDTH))
        fout.write('\n\n')

        # Output balance and totals
        balance = accounts.get_balance(acct_name)
        if balance < 0:
            balance = '-' + locale.currency(-1 * balance, grouping=True)
        else:
            balance = locale.currency(balance, grouping=True)
        fout.write(('Current Balance: ' + balance).center(REPORT_WIDTH))

        sql = 'SELECT TOTAL(amount) FROM transactions WHERE credit = {} AND acct = "{}" AND recorded_on LIKE "{}-%%"'
        cur = db.cursor()
        total_income = cur.execute(sql.format(0, acct_name, datetime.now().strftime('%Y-%m'))).fetchone()[0]
        total_expenses = cur.execute(sql.format(1, acct_name, datetime.now().strftime('%Y-%m'))).fetchone()[0]
        total_revenue = total_income - total_expenses

        fout.write('\n')
        fout.write(('Total Income: ' + locale.currency(total_income, grouping=True)).center(REPORT_WIDTH))
        fout.write('\n')
        fout.write(('Total Expenses: ' + locale.currency(total_expenses, grouping=True)).center(REPORT_WIDTH))
        fout.write('\n')
        if total_revenue < 0:
            total_revenue = '-' + locale.currency(-1 * total_revenue, grouping=True)
        else:
            total_revenue = locale.currency(total_revenue, grouping=True)
        fout.write(('Total Revenue: ' + total_revenue).center(REPORT_WIDTH))
        fout.write('\n\n')
        fout.write('-' * REPORT_WIDTH)
        fout.write('\n\n')
        fout.write('Budgets'.center(REPORT_WIDTH))
        fout.write('\n\n')

        # Output the budgets table
        budget_month = datetime.now().strftime('%Y-%m')

        # Loop through budgets, and for the account that is attached to it
        # loop through its transactions, matching the budget category;
        # then evaluate the budget result (overbudget or underbudget)
        budget_cur = db.cursor()
        trans_cur = db.cursor()
        rows = []
        for budget in budget_cur.execute('SELECT category_name, budget_amount, budget_acct \
            FROM budget_categories WHERE month = "{}"'.format(budget_month)):
            result = budget[1] # Budget amount
            transaction_query = 'SELECT credit, amount FROM transactions \
                WHERE acct = "{}" AND budget_category = "{}" AND recorded_on LIKE "{}"'
            transaction_query = transaction_query.format(
                budget[2], budget[0], budget_month + '%')

            for transaction in trans_cur.execute(transaction_query):
                if transaction[0] == 1:
                    result -= transaction[1]
            if result > 0: # Good; means budget has not run out
                result = '+' + locale.currency(result, grouping=True)
            else:
                result = '-' + locale.currency(-1 * result, grouping=True)
            rows.append([budget[0], locale.currency(budget[1], grouping=True), result])

        table_lines = tabulate(rows, headers=['Category', 'Budget', 'Balance'], tablefmt='psql').split('\n')
        for line in table_lines:
            fout.write(line.center(REPORT_WIDTH))
            fout.write('\n')
        fout.write('\n\n')
        fout.write('-' * REPORT_WIDTH)
        fout.write('\n\n')
        fout.write('Transactions'.center(REPORT_WIDTH))
        fout.write('\n\n')

        # Output the transactions table
        cur.execute('SELECT trans_id, description, credit, amount, budget_category, \
            recorded_on FROM transactions WHERE acct = "{}" ORDER BY recorded_on \
            DESC'.format(acct_name))
        rows = cur.fetchall()

        # Place (+/-) in front of amount in response to credit/debit
        new_rows = []
        for row in rows:
            str_amount = ''
            if row[2] == 1: # Credit
                str_amount = '-' + str(locale.currency(row[3], grouping=True))
            else:
                str_amount = '+' + str(locale.currency(row[3], grouping=True))
            new_rows.append(row[:2] + (str_amount,) + row[3:])

        table_lines = tabulate(
            new_rows,
            headers=[
                'Transaction #', 'Description',
                'Amount', 'Category', 'Recorded On'],
            tablefmt='psql'
        ).split('\n')

        for line in table_lines:
            fout.write(line.center(REPORT_WIDTH))
            fout.write('\n')

