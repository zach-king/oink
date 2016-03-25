import sqlite3


path = None
conn = None
cursor = None


def connect():
    if not path:
        raise Exception('Sqlite path not set')


def execute():
    """
    Lazy loads a sqlite3 connection and cursor.

    """
    pass