import unittest

from oink import utils


class TestAccounts(unittest.TestCase):
    def test_strpmoney_converts_to_atomic_value(self):
        s_money = '9.97'
        i_money = utils.strpmoney(s_money)
        self.assertEqual(i_money, 997)

    def test_strfmoney_formats_atomic_value_to_decimal_string(self):
        i_money = 997
        s_money = utils.strfmoney(i_money)
        self.assertEqual(s_money, '9.97')


if __name__ == '__main__':
    unittest.main()
