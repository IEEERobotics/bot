"""Test cases for planner."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import planner.planner as p_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestExecStrategy(test_bot.TestBot):

    """Test executing strategies."""

    def setUp(self):
        """Setup test hardware files and build planner object."""
        # Run general bot test setup
        super(TestExecStrategy, self).setUp()

        # Store original strategy file
        self.orig_strat_file = self.config["strategy"]

    def tearDown(self):
        """Restore testing flag state and strategy in config file."""
        # Run general bot test tear down
        super(TestExecStrategy, self).tearDown()

        # Restore original strategy file
        lib.set_strat_qual(self.orig_strat_file)

    def test_empty(self):
        """Test planner's handling of an empty strategy file."""
        lib.set_strat("test_empty.yaml")
        with self.assertRaises(AssertionError):
            p_mod.Planner()

    def test_follow_intersectionEx(self):
        """Test a follow action with an expected IntersectionException.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_follow_intersectionEx.yaml")
        p_mod.Planner()

    def test_follow_boxEx(self):
        """Test a follow action with an expected BoxException.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_follow_boxEx.yaml")
        p_mod.Planner()

    @unittest.expectedFailure
    def test_rote_move(self):
        """Test a rote move action.

        This test fails because mec_driver doesn't override driver's move
        method. The move method should accept a command string and handle it
        as a rote move or a command from follower.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_rote_move.yaml")
        p_mod.Planner()

    def test_fire(self):
        """Test a fire action.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_fire.yaml")
        p_mod.Planner()
