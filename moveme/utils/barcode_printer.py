# coding=utf-8

"""
barcode_printer.py is responsible for [brief description here].
"""
import cups
import os
import re
import barcode
from barcode.writer import ImageWriter
import yaml

class BarcodePrinter(object):

    def __init__(self, printer_name):
        self.printer_conn = cups.Connection()
        self.code39 = barcode.get_barcode_class('code39')
        self.printer = printer_name

    def print_barcode(self, string, callback=None):
        bc = self.code39(string, writer=ImageWriter(), add_checksum=False).save(string)
        self.printer_conn.printFile(self.printer, bc, "Label for %s" % string, options={})
        os.remove(bc)

        if callback:
            callback()