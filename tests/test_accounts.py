'''
File: test_accounts.py
Author: Zachary King

Defines unit tests for accounts.py.
Tests all account features.
'''

from __future__ import print_function

import unittest, os
import sqlite3

from oink import accounts, db


class TestAccounts(unittest.TestCase):
    '''Defines unit tests for adding and removing accounts.'''
    
    def setUp(self):
        '''Setup testing databse.'''
        # Creates the testing database
        os.mkdir('testdb')
        with open('testdb\oink.db', 'w') as fout:
            pass
        db.connect('testdb')
        accounts.setup()

    def tearDown(self):
        '''Destroys the testing database.'''
        db.disconnect()
        os.remove('testdb\oink.db')
        os.rmdir('testdb')

    def test_add_new_account(self):
        '''Test for adding a new account.'''
        cur = db.cursor()

        # Add a new account
        accounts.add_account(12345, 'TestAddAccount', 100.00, '2017-1-1')
        self.assertEqual(cur.execute('SELECT COUNT(*) FROM accounts').fetchone()[0], 1)

        accounts.add_account(54321, 'TestAddAccount2', 0.01, '2017-1-1')
        self.assertEqual(cur.execute('SELECT COUNT(*) FROM accounts').fetchone()[0], 2)

    def test_remove_account(self):
        '''Test to remove an existing account.'''
        cur = db.cursor()

        # Insert a new account
        cur.execute('INSERT INTO accounts VALUES (024, "TestRemoveAccount", 0.00, "2017-1-1")')
        self.assertEqual(cur.rowcount, 1)

        # Remove the accont
        accounts.delete('TestRemoveAccount')
        cur.execute('SELECT COUNT(*) FROM accounts')
        self.assertEqual(cur.fetchone()[0], 0)




if __name__ == '__main__':
    unittest.main()