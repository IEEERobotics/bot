"""Module for unittest parent class."""

import unittest

import bot.lib.lib as lib
import bot.simulator.sim_hw_builder as sim_hw_builder_mod


def additional_tests():
    return unittest.defaultTestLoader.discover("..")


class TestBot(unittest.TestCase):

    """Test class that all bot unittets should subclass."""

    def setUp(self):
        """Get config, set simulation pins to known state, set test flag."""
        # Load config and logger
        self.config = lib.get_config("bot/config.yaml")
        self.logger = lib.get_logger()

        # Set testing flag in config
        self.orig_test_state = self.config["testing"]
        lib.set_testing(True)

        # Write known values to all simulated hardware files
        sim_hw_builder = sim_hw_builder_mod.SimHWBuilder()
        sim_hw_builder.build_all_hw()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)
