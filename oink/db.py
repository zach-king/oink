'''
File: db.py
'''

from __future__ import print_function
import os

import sqlite3


conn = None


def connect(path):
    '''
    Connect to the sqlite database provided at the specified path.
    '''
    global conn
    conn = sqlite3.connect(os.path.join(path, 'oink.db'))
    if os.environ.get('DEBUG', ''):
        conn.set_trace_callback(print) # prints queries; useful for development

    # Enable foreign key support
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON')
    if cur.rowcount == 0:
        print('Failed to enable foreign key support. Failed to connect to database.')
        exit(1)
    return conn


def cursor():
    '''
    Returns a sqlite3 cursor to the database
    '''
    return conn.cursor()


def commit():
    '''
    Commit the changes to the database.
    '''
    return conn.commit()


def disconnect():
    '''
    Close the connection to the databse.
    '''
    return conn.close()
