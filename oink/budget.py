'''
File: budget.py
'''

from __future__ import print_function

from . import db


def setup():
    '''
    Setup budgeting table(s).
    '''
    cur = db.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS budget_categories (name)')
    db.commit()
