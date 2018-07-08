#!/usr/bin/python3
"""
File: _txt.py
Author: Zachary King

Implements the .txt report generation for Oink
"""

from datetime import datetime
import locale

from tabulate import tabulate

from .. import accounts, db, transactions
from . import reports

REPORT_WIDTH = 100

def generate_report(from_date, to_date, filepath):
    """
    Generates a text Oink report
    """
    report = reports.generate_report_data(from_date, to_date)

    def hr(num_newlines=1):
        fout.write('-' * REPORT_WIDTH + '\n' * num_newlines)

    def br(num_newlines=1):
        fout.write('\n' * num_newlines)

    def header(text):
        hr(1)
        fout.write(text.center(REPORT_WIDTH) + '\n')
        hr(1)

    def subheader(text):
        fout.write(f'[ {text} ]'.center(REPORT_WIDTH) + '\n')

    def write(text, trailing_newlines=1, alignment=''):
        if alignment.upper() == 'LEFT':
            fout.write(text.ljust(REPORT_WIDTH) + '\n' * trailing_newlines)
        elif alignment.upper() == 'RIGHT':
            fout.write(text.rjust(REPORT_WIDTH) + '\n' * trailing_newlines)
        elif alignment.upper() == 'CENTER':
            fout.write(text.center(REPORT_WIDTH) + '\n' * trailing_newlines)
        else:
            fout.write(text + '\n' * trailing_newlines)

    def write_cols(text_list, trailing_newlines=1, alignments=[]):
        n = len(text_list)
        spacing = REPORT_WIDTH // n
        if not alignments:
            alignments = ['CENTER' for _ in text_list]
        for i, text in enumerate(text_list):
            write(text, 0, alignments[i])
        br(trailing_newlines)

    with open(filepath, 'w') as fout:
        hr(2)
        write('OINK REPORT', 2, 'center')
        write('Generated at ' + report['report']['created_at'] + ' for ' + report['report']['from_date'] + ' to ' + report['report']['to_date'], alignment='center')
        hr(2)

        header('Accounts')

        for account_id, account in report['accounts'].items():
            write(f'Account Name: {account["name"]}', alignment='left')
            write(f'Account #{account["account_number"]}', alignment='left')
            write(f'Balance: {account["balance"]}', alignment='left')
            write(f'Created At: {account["created_at"]}', 2, 'left')

            write(f'Total Income  : {account["total_income"]}')
            write(f'Total Expenses: {account["total_expenses"]}')
            write(f'Total Revenue : {account["total_revenue"]}', 2)

            subheader('Transactions')
            br()

            # Write transactional data for account
            if account['transactions']:
                rows = []
                for trans in account['transactions'].values():
                    if trans['type']['id'] == transactions.WITHDRAWAL_ID:
                        trans['amount'] = '-' + trans['amount']
                    elif trans['type']['id'] == transactions.DEPOSIT_ID:
                        trans['amount'] = '+' + trans['amount']

                    rows.append([
                        trans["id"],
                        trans['category']['name'],
                        trans['amount'],
                        trans['created_at'],
                    ])
                headers = ['Transaction #', 'Category', 'Amount', 'Created At',]
                fout.write(tabulate(rows, headers=headers, tablefmt='psql', stralign='right'))
            else:
                write('< No transactions for this account >', alignment='center')

            br(2)
            subheader('Budgets')
            br()

            # Write budget data for account
            if account['budgets']:
                rows = []
                headers = ['ID', 'Category', 'Year', 'Month', 'Amount', 'Balance', 'Created At',]
                for bud in account['budgets'].values():
                    rows.append([
                        bud['id'],
                        bud['category']['name'],
                        bud['year'],
                        bud['month'],
                        bud['amount'],
                        bud['balance'],
                        bud['created_at'],
                    ])
                fout.write(tabulate(rows, headers=headers, tablefmt='psql', stralign='right'))
            else:
                write('< No budgets for this account yet >', alignment='center')

            br(2)
            hr(2)

    #
    # with open(filepath, 'w') as fout:
    #     # Write the header info (date & account info)
    #     fout.write('-' * REPORT_WIDTH + '\n\n')
    #     fout.write('OINK REPORT'.center(REPORT_WIDTH))
    #     fout.write('\n\n')
    #     fout.write(('Generated on ' + datetime.now().strftime('%Y-%m-%d') + ' for the month of ' + datetime.now().strftime('%Y-%m')).center(REPORT_WIDTH))
    #     fout.write('\n')
    #     fout.write('-' * REPORT_WIDTH + '\n\n')
    #
    #     fout.write(('Account: ' + acct_name).center(REPORT_WIDTH))
    #     fout.write('\n')
    #     fout.write(('Account #' + str(acct_no)).center(REPORT_WIDTH))
    #     fout.write('\n\n')
    #
    #     # Output balance and totals
    #     balance = accounts.get_balance(acct_name)
    #     if balance < 0:
    #         balance = '-' + locale.currency(-1 * balance, grouping=True)
    #     else:
    #         balance = locale.currency(balance, grouping=True)
    #     fout.write(('Current Balance: ' + balance).center(REPORT_WIDTH))
    #
    #     sql = 'SELECT TOTAL(amount) FROM transactions WHERE credit = {} AND acct = "{}" AND recorded_on LIKE "{}-%%"'
    #     cur = db.cursor()
    #     total_income = cur.execute(sql.format(0, acct_name, datetime.now().strftime('%Y-%m'))).fetchone()[0]
    #     total_expenses = cur.execute(sql.format(1, acct_name, datetime.now().strftime('%Y-%m'))).fetchone()[0]
    #     total_revenue = total_income - total_expenses
    #
    #     fout.write('\n')
    #     fout.write(('Total Income: ' + locale.currency(total_income, grouping=True)).center(REPORT_WIDTH))
    #     fout.write('\n')
    #     fout.write(('Total Expenses: ' + locale.currency(total_expenses, grouping=True)).center(REPORT_WIDTH))
    #     fout.write('\n')
    #     if total_revenue < 0:
    #         total_revenue = '-' + locale.currency(-1 * total_revenue, grouping=True)
    #     else:
    #         total_revenue = locale.currency(total_revenue, grouping=True)
    #     fout.write(('Total Revenue: ' + total_revenue).center(REPORT_WIDTH))
    #     fout.write('\n\n')
    #     fout.write('-' * REPORT_WIDTH)
    #     fout.write('\n\n')
    #     fout.write('Budgets'.center(REPORT_WIDTH))
    #     fout.write('\n\n')
    #
    #     # Output the budgets table
    #     budget_month = datetime.now().strftime('%Y-%m')
    #
    #     # Loop through budgets, and for the account that is attached to it
    #     # loop through its transactions, matching the budget category;
    #     # then evaluate the budget result (overbudget or underbudget)
    #     budget_cur = db.cursor()
    #     trans_cur = db.cursor()
    #     rows = []
    #     for budget in budget_cur.execute('SELECT category_name, budget_amount, budget_acct \
    #         FROM budget_categories WHERE month = "{}"'.format(budget_month)):
    #         result = budget[1] # Budget amount
    #         transaction_query = 'SELECT credit, amount FROM transactions \
    #             WHERE acct = "{}" AND budget_category = "{}" AND recorded_on LIKE "{}"'
    #         transaction_query = transaction_query.format(
    #             budget[2], budget[0], budget_month + '%')
    #
    #         for transaction in trans_cur.execute(transaction_query):
    #             if transaction[0] == 1:
    #                 result -= transaction[1]
    #             else:
    #                 result += transaction[1]
    #         if result > 0: # Good; means budget has not run out
    #             result = '+' + locale.currency(result, grouping=True)
    #         else:
    #             result = '-' + locale.currency(-1 * result, grouping=True)
    #         rows.append([budget[0], locale.currency(budget[1], grouping=True), result])
    #
    #     table_lines = tabulate(rows, headers=['Category', 'Budget', 'Balance'], tablefmt='psql').split('\n')
    #     for line in table_lines:
    #         fout.write(line.center(REPORT_WIDTH))
    #         fout.write('\n')
    #     fout.write('\n\n')
    #     fout.write('-' * REPORT_WIDTH)
    #     fout.write('\n\n')
    #     fout.write('Transactions'.center(REPORT_WIDTH))
    #     fout.write('\n\n')
    #
    #     # Output the transactions table
    #     cur.execute('SELECT trans_id, description, credit, amount, budget_category, \
    #         recorded_on FROM transactions WHERE acct = "{}" ORDER BY recorded_on \
    #         DESC'.format(acct_name))
    #     rows = cur.fetchall()
    #
    #     # Place (+/-) in front of amount in response to credit/debit
    #     new_rows = []
    #     for row in rows:
    #         str_amount = ''
    #         if row[2] == 1: # Credit
    #             str_amount = '-' + str(locale.currency(row[3], grouping=True))
    #         else:
    #             str_amount = '+' + str(locale.currency(row[3], grouping=True))
    #         new_rows.append(row[:2] + (str_amount,) + row[3:])
    #
    #     table_lines = tabulate(
    #         new_rows,
    #         headers=[
    #             'Transaction #', 'Description',
    #             'Amount', 'Category', 'Recorded On'],
    #         tablefmt='psql'
    #     ).split('\n')
    #
    #     for line in table_lines:
    #         fout.write(line.center(REPORT_WIDTH))
    #         fout.write('\n')
