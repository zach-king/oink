'''
File: reports.py
Author: Zachary King

Contains handlers for reporting commands. 
Reports curated budgeting information to file.
'''

from . import accounts, budget, transactions, db

import os

from tabulate import tabulate


VALID_FORMATS = ('txt', 'csv', 'pdf', 'html')


def report(acct, path, fmt='txt'):
    '''Root handler for the report command'''
    if not accounts.exists(acct):
        print('Account `{}` does not exist.'.format(acct))
        return

    # Check if file exists already
    if path == '' or path is None:
        print('Invalid file path given')
        return

    dirpath, filepath = os.path.split(path)
    if dirpath == '': # File in same directory
        if os.path.isfile(filepath):
            certain = input('The file `{}` already exists.'.format(filepath) + \
                ' Are you sure you want to overwrite it? (y/n): ').lower()
            if not certain:
                print('Report generation cancelled')
                return
        else:
            with open(path, 'w'):
                pass

    else: # Directory path was given
        if not os.path.isfile(path):
            with open(path, 'w'):
                pass
        else:
            certain = input('The file `{}` already exists.'.format(path) + \
                ' Are you sure you want to overwrite it? (y/n): ').lower()
            if not certain:
                print('Report generation canceleld')
                return

    fmt = fmt.lower()
    if fmt not in VALID_FORMATS:
        print('Unsupported report format `{}`'.format(fmt))
        print('Supported formats are ' + ','.join([f.upper() for f in VALID_FORMATS]))
        return

    if fmt == 'txt':
        _report_txt(acct, path)
    elif fmt == 'csv':
        _report_csv(acct, path)
    elif fmt == 'html':
        _report_html(acct, path)
    elif fmt == 'pdf':
        _report_pdf(acct, path)
    else:
        print('Unable to generate report')
        return


def _report_txt(acct, path):
    pass


def _report_csv(acct, path):
    pass


def _report_html(acct, path):
    pass


def _report_pdf(acct, path):
    pass
