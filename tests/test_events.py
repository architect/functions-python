# -*- coding: utf-8 -*-
import unittest
import os
import sys
import types

# just a hop, skip and a jump away..
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import arc.events 
import helper

class ArcEventsTest(unittest.TestCase):

    def setUp(self):
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter('ignore')

    def test_publish(self):
        val = arc.events.publish(name='ping', payload={'python':True})
        self.assertTrue(val)

if __name__ == '__main__':
    unittest.main()
