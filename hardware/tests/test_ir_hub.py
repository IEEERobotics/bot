"""Test cases for IRHub abstraction class."""
import sys
import os
import unittest
import random

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


class TestSelectNthUnits(test_bot.TestBot):

    """Test selecting IR units to be read."""

    def setUp(self):
        """Get config and built IRHub object."""
        # Run general bot test setup
        super(TestSelectNthUnits, self).setUp()

        # Built IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestSelectNthUnits, self).tearDown()

    def test_all_valid_n(self):
        """Loop over every valid value for n."""
        gpio_select_nums = self.config["ir_select_gpios"]
        for n in range(0, self.ir_hub.num_ir_units):
            self.ir_hub.select_nth_units(n)
            line_val = "{:04b}".format(n)
            for gpio_num, expected_val in zip(gpio_select_nums, line_val):
                observed_val = int(self.get_gpio(gpio_num)["value"])
                assert int(expected_val) == observed_val

    def test_n_max(self):
        """Confirm that values at max are accepted."""
        self.ir_hub.select_nth_units(self.ir_hub.num_ir_units - 1)

    def test_n_min(self):
        """Confirm that values at min are accepted."""
        self.ir_hub.select_nth_units(0)

    def test_n_over_max(self):
        """Confirm that values over max are rejected."""
        with self.assertRaises(ValueError):
            self.ir_hub.select_nth_units(self.ir_hub.num_ir_units + 1)

    def test_n_under_min(self):
        """Confirm that values under min are rejected."""
        with self.assertRaises(ValueError):
            self.ir_hub.select_nth_units(-1)


class TestReadNthUnits(test_bot.TestBot):

    """Test reading IR units."""

    def setUp(self):
        """Get config and built IRHub object."""
        # Run general bot test setup
        super(TestReadNthUnits, self).setUp()

        # Built IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestReadNthUnits, self).tearDown()

    def gen_random_read_vals(self):
        """Sets simulated read GPIOs of each array to known, random val."""
        set_vals = {}
        for name, gpio in self.ir_hub.arrays.iteritems():
            set_vals[name] = random.randint(0, 1)
            self.setup_gpio(gpio, value=str(set_vals[name]) + "\n")
        return set_vals

    @unittest.skip("Something's broken about this test. Still working on it.")
    def test_all_valid_n(self):
        """Loop over every valid value for n."""
        for array_reading in self.ir_hub.reading.values():
            assert len(array_reading) == self.ir_hub.num_ir_units
            for unit_reading in array_reading:
                assert unit_reading == 0

        for n in range(0, self.ir_hub.num_ir_units):
            expected_vals = self.gen_random_read_vals()
            self.ir_hub.select_nth_units(n)
            for name, array_reading in self.ir_hub.reading.iteritems():
                observed_val = array_reading[n]
                assert observed_val == expected_vals[name], \
                       "{} != {}".format(observed_val, expected_vals[name])

    def test_n_max(self):
        """Confirm that values at max are accepted."""
        self.ir_hub.read_nth_units(self.ir_hub.num_ir_units - 1)

    def test_n_min(self):
        """Confirm that values at min are accepted."""
        self.ir_hub.read_nth_units(0)

    def test_n_over_max(self):
        """Confirm that values over max are rejected."""
        with self.assertRaises(ValueError):
            self.ir_hub.read_nth_units(self.ir_hub.num_ir_units + 1)

    def test_n_under_min(self):
        """Confirm that values under min are rejected."""
        with self.assertRaises(ValueError):
            self.ir_hub.read_nth_units(-1)


class TestReadAll(test_bot.TestBot):

    """Test selecting and reading all IR units on all arrays."""

    def setUp(self):
        """Get config and built IRHub object."""
        # Run general bot test setup
        super(TestReadAll, self).setUp()

        # Built IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestReadAll, self).tearDown()

    def testStructure(self):
        """Confirm that IRHub behavior is as expected."""
        readings = self.ir_hub.read_all()
        assert type(readings) is dict, \
            "IR hub readings type: {}".format(type(reading))
        for name, reading in readings.iteritems():
            assert type(name) is str
            assert type(reading) is list
            for ir_value in reading:
                assert ir_value == 0
