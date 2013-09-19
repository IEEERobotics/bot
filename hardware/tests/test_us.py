"""Test cases for ultrasonic abstraction class."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.us as us_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()

class TestDistance(unittest.TestCase):

    """Test reading ultrasonic distance values."""

    def setUp(self):
        """Get config and built US object."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Built ultrasonic abstraction object
        self.us = us_mod.US("test")

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def testStub(self):
        """Confirm that stub behavior is working as expected."""
        assert self.us.distance == 0
