import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path
try:
    import lib.lib as lib
    import follower.pid_follower as f_mod
    import planner.fsm_planner as fsm
    import tests.test_bot as test_bot    
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestPIDFollower(test_bot.TestBot):

    """Test Follower."""
    
    def setUp(self):
        """Get config and built IR object."""
        super(TestPIDFollower, self).setUp()

        # Build Follower object
        self.follower = f_mod.PIDFollower() 
        self.state = fsm.StateTable()
        
    def tearDown(self):
        """Restore testing flag state in config file."""
        super(TestPIDFollower, self).tearDown()
    
    def testFollower(self):
        self.state.currentHeading = 0
        self.follower.follow(self.state)
        
        
