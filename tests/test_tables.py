# -*- coding: utf-8 -*-
import unittest
import os
import sys
import types

# just a hop, skip and a jump away..
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import arc.tables
import helper

class ArcTablesTest(unittest.TestCase):

    def setUp(self):
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter('ignore')

    def test_tables(self):
        val = arc.tables.name(table='noises')
        print(val)
        tbl = arc.tables.table(table='noises')
        print(dir(tbl))
        self.assertTrue(val)

if __name__ == '__main__':
    unittest.main()
