#!/usr/bin/env python3

"""
File: category.py
"""

from __future__ import print_function
import re
from datetime import datetime
import locale

# 3rd-Party module for tabular console output
from tabulate import tabulate

from . import db, utils
from .colorize import colorize, colorize_headers, colorize_list
from .colorize import color_input, color_error, color_info, color_success


class Category(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


def setup():
    """
    Initial database setup; creates the `accounts` table
    """
    locale.setlocale(locale.LC_ALL, '')
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id integer NOT NULL PRIMARY KEY,
            name text NOT NULL UNIQUE);
        ''')
    db.commit()


def list_all():
    """
    Lists all the available categories
    """
    categories = db.cursor().execute('SELECT id, name FROM categories ORDER BY name').fetchall()

    headers = colorize_headers(['ID', 'Name'])
    print(tabulate(categories, headers=headers, tablefmt='psql'))


def new(name):
    """
    Handler for creating a new category.
    """
    if create(name):
        print(color_success(f'"{name}" category created'))
    else:
        print(color_error(f'"{name}" category already exists'))


def rename(old_name, new_name):
    """
    Handler for renaming category `old_name` to `new_name`
    """
    if exists(old_name):
        if (exists(new_name)):
            print(color_error(f'"{new_name}" category already exists'))
        else:
            old_id, old_name = get_by_name(old_name)
            if update(old_id, new_name):
                print(color_success(f'Renamed category "{old_name}" to "{new_name}"'))
            else:
                print(color_error(f'Unable to rename category "{old_name}" to "{new_name}"'))
    else:
        print(color_error(f'"{old_name}" category does not exist'))


def remove(_id):
    """
    Handler for deleting a category
    """
    if get(_id):
        conf = input(color_input('Are you sure you want to delete this category? [y/n] '))
        if conf.lower() != 'y':
            print(color_info('Aborted category deletion'))
            return

        if delete(_id):
            print(color_success(f'Category (ID: {_id}) deleted'))
        else:
            print(color_error(f'Unable to delete category'))
    else:
        print(color_error(f'Category (ID: {_id}) does not exist'))


def get(id):
    """
    Fetches a category by `id`
    """
    return db.cursor().execute('SELECT id, name FROM categories WHERE id = ?', (id,)).fetchone()


def get_by_name(name):
    """
    Fetches a category by its `name`
    """
    return db.cursor().execute('SELECT id, name FROM categories WHERE name = ?', (name,)).fetchone()


def create(name):
    """
    Create a new category named `name`.
    Returns `True` if successful; `False` otherwise.
    """
    if exists(name):
        return False
    db.cursor().execute('INSERT INTO categories (name) VALUES (?)', (name,))
    db.commit()
    return True


def update(id, name):
    """
    Sets the name of category `id` to `name`.
    """
    cur = db.cursor()
    cur.execute('UPDATE categories SET name = ? WHERE id = ?', (name, id))
    db.commit()
    return cur.rowcount == 1


def delete(id):
    """
    Deletes the category by `id`
    """
    cur = db.cursor()
    cur.execute('DELETE FROM categories WHERE id = ?', (id,))
    db.commit()
    return cur.rowcount == 1


def exists(name):
    """
    `True` if a category named `name` exists;
    `False` otherwise.
    """
    return db.cursor().execute('SELECT COUNT(*) FROM categories WHERE name = ?', (name,)).fetchone()[0] != 0


def print_list():
    """
    Prints out the available categories
    """
    cats = db.cursor().execute('SELECT id, name FROM categories ORDER BY id').fetchall()
    headers = colorize_headers(['ID', 'Name'])
    print(tabulate(cats, headers=headers, tablefmt='psql'))
