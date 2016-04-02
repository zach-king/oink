import os

import sqlite3


conn = None


def connect(path):
    global conn
    conn = sqlite3.connect(os.path.join(path, 'oink.db'))


def cursor():
    return conn.cursor()


def commit():
    return conn.commit()


def disconnect():
    return conn.close()