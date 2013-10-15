"""Test cases for IR abstraction class."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.ir as ir_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestReading(unittest.TestCase):

    """Test reading IR sensor values using IR abstraction."""

    def setUp(self):
        """Get config and built IR object."""
        # Load config
        config = lib.load_config()
        gpio_test_dir_base = config["test_gpio_base_dir"]
        adc_test_dir = config["test_adc_base_dir"]

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Create GPIO test directories if they don't exist
        for gpio in config["ir_select_gpios"]:
            gpio_test_dir = gpio_test_dir_base + str(gpio)
            if not os.path.exists(gpio_test_dir):
                os.makedirs(gpio_test_dir)

            # Set known values in GPIO simulated hardware files
            with open(gpio_test_dir + "/value", "w") as f:
                f.write("0\n")
            with open(gpio_test_dir + "/direction", "w") as f:
                f.write("out\n")

        # Create ADC test directory if it doesn't exist
        if not os.path.exists(adc_test_dir):
            os.makedirs(adc_test_dir)

        # Set known value in ADC simulated hardware files
        ir_input_adcs = config["ir_input_adcs"]
        for name, pin in ir_input_adcs.iteritems():
            sim_file = adc_test_dir + "/AIN" + str(pin)
            with open(sim_file, "w") as f:
                f.write("0\n")

        # Build IR array objects
        self.arrays = {}
        for name, pin in ir_input_adcs.iteritems():
            self.arrays[name] = ir_mod.IRArray(name, pin)

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def testStub(self):
        """Confirm that stub behavior is working as expected."""
        for name, array in self.arrays.iteritems():
            reading = array.read_all_units()
            assert type(reading) is list, "IR array: {}, type: {}".format(
                name, type(reading))
            for ir_value in reading:
                assert ir_value == 0
