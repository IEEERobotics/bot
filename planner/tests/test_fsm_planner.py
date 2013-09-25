"""Test cases for fsm planner."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import planner.fsm_planner as fsm_mod
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise

# Logger object
logger = lib.get_logger()


class TestFSM(unittest.TestCase):
    """Test rotation of mec wheels"""

    def setUp(self):
        """Setup test hardware files and create mec_driver object"""
        config = lib.load_config()

        # Store original test flag, set to true
        self.orig_test_state = config["testing"]
        #print config["testing"]
        lib.set_testing(True)
        #print config["testing"]

        # Build fsm_planner
        self.fsm = fsm_mod.Robot()
        
    def testBaseCase(self):
        self.fsm.run()
        
    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)
