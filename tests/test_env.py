# -*- coding: utf-8 -*-
import unittest
import os
import sys
import types

# just a hop, skip and a jump away..
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import arc.events 
import arc.http
import arc.queues
import arc.tables
import arc.ws

class ArcTest(unittest.TestCase):
    def test_env(self):
        self.assertTrue(isinstance(arc.events, types.ModuleType))
        self.assertTrue(isinstance(arc.http, types.ModuleType))
        self.assertTrue(isinstance(arc.queues, types.ModuleType))
        self.assertTrue(isinstance(arc.tables, types.ModuleType))
        self.assertTrue(isinstance(arc.ws, types.ModuleType))

if __name__ == '__main__':
    unittest.main()
