# -*- coding: utf-8 -*-
import unittest
import os
import sys
import types

# just a hop, skip and a jump away..
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import arc.queues
import helper

class ArcQueuesTest(unittest.TestCase):

    def setUp(self):
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter('ignore')

    def test_queue_publish(self):
        val = arc.queues.publish(name='continuum', payload={'python':True})
        self.assertTrue(val)

if __name__ == '__main__':
    unittest.main()
