"""Test cases for IRHub abstraction class."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.ir_hub as ir_hub_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestReadings(test_bot.TestBot):

    """Test reading IR sensor values using IRHub abstraction."""

    def setUp(self):
        """Get config and built IRHub object."""
        # Run general bot test setup
        super(TestReadings, self).setUp()

        # Built IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        lib.set_testing(self.orig_test_state)

    def testIRHub(self):
        """Confirm that IRHub behavior is as expected."""
        readings = self.ir_hub.read_all()
        assert type(readings) is dict, \
            "IR hub readings type: {}".format(type(reading))
        for name, reading in readings.iteritems():
            assert type(name) is str
            assert type(reading) is list
            for ir_value in reading:
                assert ir_value == 0
