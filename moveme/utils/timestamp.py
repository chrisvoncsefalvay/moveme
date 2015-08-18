# coding=utf-8


"""
timestamp is responsible for [brief description here].
"""

from datetime import datetime

def make_timestamp():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
