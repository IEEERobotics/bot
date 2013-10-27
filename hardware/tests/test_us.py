"""Test cases for ultrasonic abstraction class."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.us as us_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestDistance(test_bot.TestBot):

    """Test reading ultrasonic distance values."""

    def setUp(self):
        """Get config and built US object."""
        # Run general bot test setup
        super(TestDistance, self).setUp()

        # Built ultrasonic abstraction object
        us = self.config["ultrasonics"][0]
        self.us = us_mod.US(us["position"], us["GPIO"])

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestDistance, self).tearDown()

    def testStub(self):
        """Confirm that stub behavior is working as expected."""
        assert self.us.distance == 0
