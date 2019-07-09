# -*- coding: utf-8 -*-
import unittest
import os
import sys
import types

# just a hop, skip and a jump away..
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import arc
import helper

class ArcReflectTest(unittest.TestCase):

    def setUp(self):
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter('ignore')

    def test_arc_reflect(self):
        val = arc.reflect()
        print(val)
        self.assertTrue(val)

if __name__ == '__main__':
    unittest.main()
