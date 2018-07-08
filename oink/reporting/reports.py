"""
File: reports.py
Author: Zachary King

Contains handlers for reporting commands.
Reports curated budgeting information to file.
"""

from .. import accounts, budget, transactions, db, colorize, category, utils
from . import _txt, _html, _json

import os
import locale
import datetime

from tabulate import tabulate

locale.setlocale(locale.LC_ALL, '')

VALID_FORMATS = ('txt', 'json',)  # TODO: add support for 'csv', 'html', 'md', 'pdf',)


def report(path, from_date, to_date='9999-99-99', fmt=None, month=datetime.datetime.now().month, year=datetime.datetime.now().year):
    """
    Root handler for the report command
    """

    # Check if file exists already
    if not path:
        print('Invalid file path given')
        return

    if fmt is None:
        print(colorize.color_warning('Report format not specified; will try to infer from file extension...'))
        try:
            fmt = os.path.split(os.path.expanduser(path))[1].split('.', 1)[1]
        except IndexError:
            print(colorize.color_error('Unable to infer the report format from file extension'))
            return

    fmt = fmt.lower()
    if fmt not in VALID_FORMATS:
        print(colorize.color_error('[error]') + ' Unsupported report format `{}`'.format(fmt))
        print('Supported formats are ' + ', '.join([f.lower() for f in VALID_FORMATS]))
        return

    if not path.lower().endswith(fmt):
        path += '.' + fmt.lower()

    path = os.path.expanduser(path)
    dirpath, filepath = os.path.split(path)
    if not dirpath: # File in same directory
        if os.path.isfile(filepath):
            overwrite = input(colorize.color_warning('File already exists. Overwrite it? (y/n): ')).lower()
            if overwrite in ('n', 'no', '0'):
                print(colorize.color_info('Report generation cancelled'))
                return
        else:
            # File doesn't exist so create it
            with open(path, 'w'):
                pass

    else: # Directory path was given
        if not os.path.isfile(path):
            with open(path, 'w'):
                pass
        else:
            overwrite = input(colorize.color_warning('File already exists. Overwrite it? (y/n): ')).lower()
            if overwrite in ('n', 'no', '0'):
                print(colorize.color_info('Report generation cancelled'))
                return

    if fmt == 'txt':
        _report_txt(from_date, to_date, path)
    elif fmt == 'json':
        _report_json(from_date, to_date, path)
    elif fmt == 'csv':
        _report_csv(acct_id, acct_name, path)
    elif fmt == 'html':
        _report_html(acct_id, acct_name, path)
    elif fmt == 'pdf':
        _report_pdf(acct_id, acct_name, path)
    else:
        print(colorize.color_error('[error]') + ' Unable to generate report')
        return
    print(colorize.color_success('Report generated and saved to `{}`'.format(path)))


def _report_txt(from_date, to_date, path):
    _txt.generate_report(from_date, to_date, path)


def _report_json(from_date, to_date, path):
    _json.generate_report(from_date, to_date, path)


def _report_csv(acct_id, acct_name, path):
    pass


def _report_html(acct_id, acct_name, path):
    # _html.generate_html_report(acct_id, acct_name, path)
    pass


def _report_pdf(acct_id, acct_name, path):
    pass


def generate_report_data(from_date, to_date):
    """
    Queries for various data on the account
    to be included in a report.
    Returns a dictionary.
    """
    data = {
        'report': {
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'from_date': from_date,
            'to_date': to_date,
        },
        'accounts': {},
    }

    cur = db.cursor()
    accts = accounts.all()

    for account in accts:
        acct_data = {
            'id': account.id,
            'account_number': account.account_number,
            'name': account.name,
            'created_at': account.created_at,
            'transactions': {},
            'budgets': {},
        }

        # Need to adjust the balance of the account to
        # reflect the balance at the end of the given `to_date`
        future_totals_query = 'SELECT SUM(amount) FROM transactions \
            WHERE account_id = ? AND transaction_type_id = ? \
            AND created_at > ?;'
        future_income = cur.execute(future_totals_query, (account.id, transactions.DEPOSIT_ID, to_date)).fetchone()[0]
        future_income = future_income if future_income is not None else 0
        future_expenses = cur.execute(future_totals_query, (account.id, transactions.WITHDRAWAL_ID, to_date)).fetchone()[0]
        future_expenses = future_expenses if future_expenses is not None else 0
        acct_data['balance'] = account.balance - future_income + future_expenses  # "Undoes" the transaction effects beyond to_date

        totals_query = 'SELECT SUM(amount) FROM transactions \
            WHERE account_id = ? AND transaction_type_id = ? \
            AND created_at BETWEEN ? AND ?;'
        total_income = cur.execute(totals_query, (account.id, transactions.DEPOSIT_ID, from_date, to_date)).fetchone()[0]
        acct_data['total_income'] = total_income if total_income is not None else 0
        total_expenses = cur.execute(totals_query, (account.id, transactions.WITHDRAWAL_ID, from_date, to_date)).fetchone()[0]
        acct_data['total_expenses'] = total_expenses if total_expenses is not None else 0
        acct_data['total_revenue'] = acct_data['total_income'] - acct_data['total_expenses']

        # Format currencies
        acct_data['balance'] = utils.format_money(acct_data['balance'])
        acct_data['total_income'] = utils.format_money(acct_data['total_income'])
        acct_data['total_expenses'] = utils.format_money(acct_data['total_expenses'])
        acct_data['total_revenue'] = utils.format_money(acct_data['total_revenue'])

        # Fetch and build transaction data for account
        transacts = transactions.list_for_account(account.id, from_date=from_date, to_date=to_date)
        for trans in transacts:
            trans_data = {
                'id': trans.id,
                'type': {
                    'id': trans.transaction_type.id,
                    'name': trans.transaction_type.name,
                },
                'description': trans.description,
                'amount': utils.format_money(trans.amount),
                'category': {
                    'id': trans.category.id,
                    'name': trans.category.name,
                },
                'created_at': trans.created_at,
            }
            acct_data['transactions'][trans.id] = trans_data

        # Fetch and build budget data for account
        buds = budget.list_for_account(account.id, from_date=from_date, to_date=to_date)
        for bud in buds:
            bud_data  = {
                'id': bud.id,
                'category': {
                    'id': bud.category.id,
                    'name': bud.category.name,
                },
                'amount': utils.format_money(bud.amount),
                'balance': utils.format_money(bud.balance),
                'year': bud.year,
                'month': bud.month,
                'created_at': bud.created_at,
            }
            acct_data['budgets'][bud.id] = bud_data

        data['accounts'][account.id] = acct_data

    return data
