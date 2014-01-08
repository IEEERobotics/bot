"""Unit tests for PIDFollower."""

import lib.lib as lib
import follower.pid_follower as f_mod
import planner.fsm_planner as fsm
import tests.test_bot as test_bot


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

    def test_get_position_lr_errors(self):
        """Test cases for get position left right for error throws.

        Test cases for, more than three array hits and for, less
        than three hits but with non adjacent hits.

        """
        # tests if get position lr throws -1 if more than 3 hits occur
        # test arrays for more than 3 hits
        fail01 = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail02 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        # test arrays for non adjacent hits
        fail03 = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        fail04 = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail05 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        # tests for more than three hits
        self.assertEquals(-1, self.follower.get_position_lr(fail01))
        self.assertEquals(-1, self.follower.get_position_lr(fail02))
        # tests for non adjacent hits
        self.assertEquals(-2, self.follower.get_position_lr(fail03))
        self.assertEquals(-2, self.follower.get_position_lr(fail04))

    def test_get_position_rl_errors(self):
        """Test cases for get position right left for errors throws"""
        # test arrays for more than three hits
        fail01 = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail02 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        # test arrays for non adjacent hits
        fail03 = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        fail04 = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail05 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        # tests for more than three hits
        self.assertEquals(-1, self.follower.get_position_rl(fail01))
        self.assertEquals(-1, self.follower.get_position_rl(fail02))
        self.assertEquals(-2, self.follower.get_position_rl(fail03))

    def test_oscillate(self):
        for i in xrange(0, 360, 90):
            self.follower.oscillate(i, 0.01)
