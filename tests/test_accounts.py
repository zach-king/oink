'''
File: test_accounts.py
Author: Zachary King

Defines unit tests for accounts.py.
Tests all account features.
'''

from __future__ import print_function

import unittest
import os

from oink import accounts, db


class TestAccounts(unittest.TestCase):
    '''Defines unit tests for adding and removing accounts.'''

    def setUp(self):
        '''Setup testing databse.'''
        # Creates the testing database
        os.mkdir('testdb')
        with open(r'testdb\oink.db', 'w') as fout:
            pass
        db.connect('testdb')
        accounts.setup()

    def tearDown(self):
        '''Destroys the testing database.'''
        db.disconnect()
        os.remove(r'testdb\oink.db')
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

    def test_add_null_account_number(self):
        '''Tests NOT NULL constraint of database for account number'''
        # Try to insert NULL as account number
        with self.assertRaises(ValueError):
            accounts.add_account(None, 'TestNullNumAccount', 0.0, '2017-1-1')

        with self.assertRaises(ValueError):
            accounts.add_account('', 'TestNullNumAccount', 0.0, '2017-1-1')

    def test_add_null_account_name(self):
        '''Tests NOT NULL constraint of database for account name'''
        # Try to insert NULL as account name
        with self.assertRaises(ValueError):
            accounts.add_account(987, None, 0.0, '2017-1-1')

        with self.assertRaises(ValueError):
            accounts.add_account(789, '', 0.0, '2017-1-1')

    def test_add_null_start_balance(self):
        '''Tests NOT NULL constraint of databse for account starting balance'''
        # Try to insert NULL as account starting balance
        with self.assertRaises(ValueError):
            accounts.add_account(111, 'TestNullStartBalanceAccount', None, '2017-1-1')

    def test_add_negative_start_balance(self):
        '''Tests inserting a negative starting balace for a new account'''
        with self.assertRaises(ValueError):
            accounts.add_account(222, 'TestNegativeStartingBalance', -100.0, '2017-1-1')

    def test_add_null_created_date(self):
        '''Tests NOT NULL constraint for account created_on'''
        with self.assertRaises(ValueError):
            accounts.add_account(333, 'TestNullCreatedOn', 0.0, '')

        with self.assertRaises(ValueError):
            accounts.add_account(333, 'TestNullCreatedOn', 0.0, None)


if __name__ == '__main__':
    unittest.main()
