#!/usr/bin/env python3

"""
File: utils.py
"""

import locale
import re


locale.setlocale(locale.LC_ALL, '')


def strpmoney(value):
    """
    Take a currency string `value` and return the
    atomic integer format (e.g. "9.97" => 997)
    """
    value = re.sub(r'[^0-9\.]', '', value)
    if '.' in value:
        whole, part = value.split('.', 1)
        whole = int(whole)
        part = int(part)
        return part + (whole * 100)
    else:
        return int(value) * 100


def strfmoney(value):
    """
    Take an atomic integer currency `value`
    and format a currency string
    (e.g. 410 => "4.10")
    """
    if isinstance(value, int):
        return str(float(value / 100))
    else:
        return str(value)
