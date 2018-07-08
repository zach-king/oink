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
