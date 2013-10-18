"""Tests cases for simple follower."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import follower.simple_follower as simple_fol_mod
    import lib.lib as lib
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestBasic(test_bot.TestBot):

    """Just get the basic code executing."""
    
    def setUp(self):
        """Setup test hardware files and build simple_follower object."""
        # Run general bot test setup
        super(TestBasic, self).setUp()

        # Build simple_follower
        self.simple_fol = simple_fol_mod.SimpleFollower()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestBasic, self).tearDown()
        
    def testBasic(self):
        """ """
        self.simple_fol.move_multi()
