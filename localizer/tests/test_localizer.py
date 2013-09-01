"""Test cases for localizer will go here"""
import sys
import os
import unittest
from random import randint
from localizer.localizer import Localizer

# Prepend this module's directory to the python path
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise

# Assing global logger object, if not already in memory
logger = lib.get_logger()

class TestGetRange(unittest.TestCase):
    def setUp(self):
        """Setup for test"""
        config = lib.load_config()

        # Store the original test flag, and set current to true
        self.orig_test_state = config["testing"]
        lib.set_testing(True)
        self.testLoc = Localizer()

    def tearDown(self):
        del self.testLoc

    def testOne(self):
        self.assertTrue(self.testLoc.getPos() == 1)
