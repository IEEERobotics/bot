"""Test cases for FSM planner."""

import lib.lib as lib
import planner.fsm_planner as fsm_mod
import tests.test_bot as test_bot


class TestFSM(test_bot.TestBot):

    """Very basic tests for FSMPlanner."""

    def setUp(self):
        """Setup test hardware files and create mec_driver object"""
        # Run general bot test setup
        super(TestFSM, self).setUp()

        # Build fsm_planner
        self.fsm = fsm_mod.Robot()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestFSM, self).tearDown()

    def testBaseCase(self):
        """Simply run through the basic solution."""
        self.fsm.run()
