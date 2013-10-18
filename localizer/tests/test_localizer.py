"""Localizer unit tests"""

import sys
import os
import unittest

# Prepend this module's directory to the python path
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    from localizer.localizer import Localizer
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise

# Assing global logger object, if not already in memory
logger = lib.get_logger()


class TestLocalizer(test_bot.TestBot):
    def setUp(self):
        """Setup for test"""
        # Run general bot test setup
        super(TestLocalizer, self).setUp()

        # Built localizer
        self.testLoc = Localizer()

    def tearDown(self):
        # Run general bot test tear down
        super(TestLocalizer, self).tearDown()

    """
    def testWhichBlock(self):
        #Should return firing position 2 when called for line 1
        pos = self.testLoc.which_block(self.testLoc.LINE_1, (11*.0254))
        #self.assertEqual(pos, 2)

        #Should return the same for firing position 3
        pos = self.testLoc.which_block(self.testLoc.LINE_1, (11*.0254))
        #self.assertEqual(pos, 2)

        #Should warn when distance greater than sensor's max is input
        pos = self.testLoc.which_block(self.testLoc.LINE_1, (100))
        #self.assertEqual(pos, 12)

        #Should warn when distance less than ultrasonic sensor's min is input
        pos = self.testLoc.which_block(self.testLoc.LINE_3, (0))
        #self.assertEqual(pos, 0)
    """
