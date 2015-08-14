# coding=utf-8

"""
uuid is responsible for [brief description here].
"""
from uuid import uuid4

def generate_UUID(type):
    uuid = uuid4().hex
    return ("%s %s-%s-%s" % (type, uuid[0:2], uuid[3:5], uuid[6:8])).upper()
