"""Test cases for ultrasonic abstraction class."""

import lib.lib as lib
import hardware.us as us_mod
import tests.test_bot as test_bot

# Build logger
logger = lib.get_logger()


class TestDistance(test_bot.TestBot):

    """Test reading ultrasonic distance values."""

    def setUp(self):
        """Get config and built US object."""
        # Run general bot test setup
        super(TestDistance, self).setUp()

        # Build ultrasonic abstraction object
        name, params = self.config["ultrasonics"].items()[0]
        self.us = us_mod.US(name, params)
        logger.info("Testing US sensor: {}".format(self.us))

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestDistance, self).tearDown()

    def testStub(self):
        """Confirm that stub behavior is working as expected."""
        self.us.update()
        assert self.us.distance == 0
