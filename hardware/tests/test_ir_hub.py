"""Test cases for IRHub abstraction class."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.ir_hub as ir_hub_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()

class TestReading(unittest.TestCase):

    """Test reading IR sensor values using IRHub abstraction."""

    def setUp(self):
        """Get config and built IRHub object."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Built IR abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def testStub(self):
        """Confirm that stub behavior is working as expected."""
        readings = self.ir_hub.read_all_arrays()
        assert type(readings) is dict, "type is {}".format(type(reading))
        for name, reading in readings.iteritems():
            assert type(name) is str
            assert type(reading) is list
            for ir_value in reading:
                assert ir_value == 0
