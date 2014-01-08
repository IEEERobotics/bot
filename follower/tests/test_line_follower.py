"""Test case for line follower"""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path
try:
    import lib.lib as lib
    import follower.line_follower as f_mod
    import planner.fsm_planner as fsm
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()
# Distance math


class TestLineFollower(test_bot.TestBot):

    """Test line Follower."""

    def setUp(self):
        """Get config and built IR object."""
        super(TestLineFollower, self).setUp()

        # Build Follower object
        self.follower = f_mod.LineFollower()
        self.state = fsm.StateTable()

    def tearDown(self):
        """Restore testing flag state in config file."""
        super(TestLineFollower, self).tearDown()

    def test_get_state_lr_errors(self):
        """Test cases for get position left right for error throws.

        Test cases for, more than three array hits and for, less
        than three hits but with non adjacent hits.

        """
        # Tests if get position lr throws -1 if more than 3 hits occur
        # Test arrays for more than 3 hits
        fail01 = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail02 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        # Test arrays for non adjacent hits
        fail03 = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        fail04 = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail05 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
        # Test arrays for high angle
        fail06 = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail07 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]
        # Test array for no line
        fail08 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # tests for more than three hits
        self.assertEquals(17, self.follower.get_position_lr(fail01))
        self.assertEquals(17, self.follower.get_position_lr(fail02))
        # tests for non adjacent hits
        self.assertEquals(19, self.follower.get_position_lr(fail03))
        self.assertEquals(19, self.follower.get_position_lr(fail04))
        self.assertEquals(19, self.follower.get_position_lr(fail05))
        # Test for high angle
        self.assertEquals(18, self.follower.get_position_lr(fail06))
        self.assertEquals(18, self.follower.get_position_lr(fail07))
        # Test for no line
        self.assertEquals(16, self.follower.get_position_lr(fail08))
        #           1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(position):
            position[index] =  1
            if(index > 0):
                position[index -1] = 0
            self.assertEquals(index * 2 - 15, self.follower.get_position_lr(position))
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(position):
            position[index] =  1
            if(index == 0):
                continue
            if(index > 1):
                position[index -2] = 0
            self.assertEquals((index - 1) * 2 - 15 + 1, self.follower.get_position_lr(position))

    def test_get_state_rl_errors(self):
        """Test cases for get position left right for error throws.

        Test cases for, more than three array hits and for, less
        than three hits but with non adjacent hits.

        """
        # Tests if get position lr throws -1 if more than 3 hits occur
        # Test arrays for more than 3 hits
        fail01 = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail02 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        # Test arrays for non adjacent hits
        fail03 = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        fail04 = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail05 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
        # Test arrays for high angle
        fail06 = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail07 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]
        # Test array for no line
        fail08 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # tests for more than three hits
        self.assertEquals(17, self.follower.get_position_rl(fail01))
        self.assertEquals(17, self.follower.get_position_rl(fail02))
        # tests for non adjacent hits
        self.assertEquals(19, self.follower.get_position_rl(fail03))
        self.assertEquals(19, self.follower.get_position_rl(fail04))
        self.assertEquals(19, self.follower.get_position_rl(fail05))
        # Test for high angle
        self.assertEquals(18, self.follower.get_position_rl(fail06))
        self.assertEquals(18, self.follower.get_position_rl(fail07))
        # Test for no line
        self.assertEquals(16, self.follower.get_position_rl(fail08))
        #           1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(position):
            position[index] =  1
            if(index > 0):
                position[index -1] = 0
            self.assertEquals(( index * 2 - 15) * -1, self.follower.get_position_rl(position))
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(position):
            position[index] =  1
            if(index == 0):
                continue
            if(index > 1):
                position[index -2] = 0
            self.assertEquals(((index - 1) * 2 - 15 + 1) * -1, self.follower.get_position_rl(position))
       

