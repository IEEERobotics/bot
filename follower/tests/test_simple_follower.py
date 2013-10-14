""" something """
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import follower.simple_follower as simple_fol_mod
    import lib.lib as lib
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestBasic(unittest.TestCase):

    """ """
    
    def setUp(self):
        """Setup test hardware files and build servo object."""
        # ID number of servo
        self.s_num = 0

        # Load config
        config = lib.load_config()
        self.test_dir = config["test_pwm_base_dir"] + str(self.s_num)

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build simple_follower
        self.simple_fol = simple_fol_mod.SimpleFollower()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)
        
    def testBasic(self):
        """ """
        self.simple_fol.move_multi()
