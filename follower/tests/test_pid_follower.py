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
# Distance math


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
        
    def test_get_postion_lr_errors(self):
	"""Test cases for get position left right for error throws

	Test cases for, more than three array hits and for, less
	than three hits but with non adjacent hits.
	"""
        # tests if get position lr throws -1 if more than 3 hits occur
        # test arrays for more than 3 hits	
        fail01 = [0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1]
        fail02 = [1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1]
        # test arrays for non adjacent hits
        fail03 = [0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0]
        fail04 = [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
        fail05 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
        # tests for more than three hits
        self.assertEquals(-1, self.follower.get_postion_lr(fail01))
        self.assertEquals(-1, self.follower.get_postion_lr(fail02))
        # tests for non adjacent hits
        self.assertEquals(-2, self.follower.get_postion_lr(fail03))
        self.assertEquals(-2, self.follower.get_postion_lr(fail04))

    def test_get_postion_rl_errors(self):
	"""Test cases for get position right left for errors throws"""
        # test arrays for more than three hits
	    fail01 = [0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1]
        fail02 = [1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1]
        # test arrays for non adjacent hits
        fail03 = [0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0]
        fail04 = [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
        fail05 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
	    # tests for more than three hits
        self.assertEquals(-1, self.follower.get_postion_rl(fail01))
        self.assertEquals(-1, self.follower.get_postion_rl(fail02))
        self.assertEquals(-2, self.follower.get_postion_rl(fail03))


