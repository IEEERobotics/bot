"""Test cases for IR abstraction class."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.ir as ir_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestIRArrays(test_bot.TestBot):

    """Test reading IR sensor values using IR array abstractions."""

    def setUp(self):
        """Get config and built IR object."""
        # Run general bot test setup
        super(TestIRArrays, self).setUp()

        # Build IR array objects
        ir_input_adcs = self.config["ir_input_adcs"]
        self.arrays = {}
        for name, pin in ir_input_adcs.iteritems():
            self.arrays[name] = ir_mod.IRArray(name, pin)

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestIRArrays, self).tearDown()

    def testIRArrays(self):
        """Confirm that IRArray behavior is as expected."""
        for name, array in self.arrays.iteritems():
            reading = array.read_all_units()
            assert type(reading) is list, \
                "IR array: {}, reading type: {}".format(name, type(reading))
            for ir_value in reading:
                assert ir_value == 0
