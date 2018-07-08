#!/usr/bin/python3
"""
File: _json.py
Author: Zachary King

Implements the .json report generation for Oink
"""

import json

from . import reports


def generate_report(from_date, to_date, filepath):
    """
    Generates a JSON Oink report for
    the date range `from_date` to `to_date`
    and saves it to a file at `filepath`.
    """
    report = reports.generate_report_data(from_date, to_date)

    with open(filepath, 'w') as fout:
        json.dump(report, fout)
