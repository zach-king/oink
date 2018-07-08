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
    if value is None:
        return 0
    value = re.sub(r'[^0-9\.]', '', value)
    if '.' in value:
        whole, part = value.split('.', 1)
        whole = int(whole)
        part = int(part)
        return part + (whole * 100)
    else:
        return int(value) * 100


def format_money(value):
    value = atomic_to_float(value)
    return locale.currency(value, grouping=True)


def strfmoney(value):
    """
    Take an atomic integer currency `value`
    and format a currency string
    (e.g. 410 => "4.10")
    """
    if value is None:
        return '0.00'
    elif isinstance(value, int):
        s = str(float(value / 100))
        if len(s.split('.', 1)[1]) == 1:
            s += '0'
        return s
    else:
        return str(value)


def atomic_to_float(value):
    """
    Transforms an atomic integer currency `value`
    into a float.
    (e.g. 695 => 6.95)
    """
    if value is None:
        return 0.0
    elif isinstance(value, int):
        return value / 100.0
    else:
        return float(value)


def float_to_atomic(value):
    """
    Take a float currency `value`
    and format it to an atomic integer
    (e.g. 4.15 => 415)
    """
    if value is None:
        return 0
    elif isinstance(value, float):
        return int(value * 100)
    else:
        return int(value)
