'''
File: reports.py
Author: Zachary King

Contains handlers for reporting commands. 
Reports curated budgeting information to file.
'''

from .. import accounts, budget, transactions, db, colorize
from . import _txt

import os

from tabulate import tabulate


VALID_FORMATS = ('txt', 'csv', 'pdf', 'html')


def report(acct, path, fmt='txt'):
    '''Root handler for the report command'''
    if not accounts.exists(acct):
        print(colorize.color_error('[error]') + ' Account `{}` does not exist.'.format(acct))
        return

    # Check if file exists already
    if path == '' or path is None:
        print('Invalid file path given')
        return

    dirpath, filepath = os.path.split(path)
    if dirpath == '': # File in same directory
        if os.path.isfile(filepath):
            overwrite = input(colorize.color_warning('File already exists. Overwrite it? (Y/N): ')).lower()
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
            overwrite = input(colorize.color_warning('File already exists. Overwrite it? (Y/N): ')).lower()
            if overwrite in ('n', 'no', '0'):
                print(colorize.color_info('Report generation cancelled'))
                return

    fmt = fmt.lower()
    if fmt not in VALID_FORMATS:
        print('Unsupported report format `{}`'.format(fmt))
        print('Supported formats are ' + ','.join([f.upper() for f in VALID_FORMATS]))
        return

    # Get account id
    cur = db.cursor()
    acct_id = cur.execute('SELECT acct_no FROM accounts WHERE name = "{}"'.format(acct)).fetchone()[0]

    if fmt == 'txt':
        _report_txt(acct_id, acct, path)
    elif fmt == 'csv':
        _report_csv(acct_id, acct, path)
    elif fmt == 'html':
        _report_html(acct_id, acct, path)
    elif fmt == 'pdf':
        _report_pdf(acct_id, acct, path)
    else:
        print('Unable to generate report')
        return


def _report_txt(acct_id, acct_name, path):
    _txt.generate_text_report(acct_id, acct_name, path)


def _report_csv(acct_id, acct_name, path):
    pass


def _report_html(acct_id, acct_name, path):
    pass


def _report_pdf(acct_id, acct_name, path):
    pass
