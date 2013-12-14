"""Test cases for IRHub abstraction class."""

import random
from time import time, sleep
import unittest

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import tests.test_bot as test_bot


class TestSelectNthUnits(test_bot.TestBot):

    """Test selecting IR units to be read."""

    def setUp(self):
        """Get config and built IRHub object."""
        # Run general bot test setup
        super(TestSelectNthUnits, self).setUp()

        # Build IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestSelectNthUnits, self).tearDown()

    # TODO: This will fail when ir_swap_halves is True, remove when corrected
    @unittest.expectedFailure
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

        # Build IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestReadNthUnits, self).tearDown()

    def gen_random_read_vals(self):
        """Sets simulated read GPIOs of each array to known, random val."""
        set_vals = {}
        for name, array in self.ir_hub.arrays.iteritems():
            gpio = array.read_gpio_pin
            set_vals[name] = random.randint(0, 1)
            self.setup_gpio(gpio, value=str(set_vals[name]) + "\n")
        return set_vals

    # NOTE: Fails when ir_read_adc is True as simulated ADC values are not set
    @unittest.expectedFailure
    def test_all_valid_n(self):
        """Loop over and read every valid value for n."""
        for array_reading in self.ir_hub.reading.values():
            assert len(array_reading) == self.ir_hub.num_ir_units
            for unit_reading in array_reading:
                assert unit_reading == 0

        for n in range(0, self.ir_hub.num_ir_units):
            expected_vals = self.gen_random_read_vals()
            self.ir_hub.read_nth_units(n)
            for name, array_reading in self.ir_hub.reading.iteritems():
                observed_val = array_reading[n]
                assert observed_val == expected_vals[name], \
                       "{} != {} for {} array".format(observed_val,
                                                      expected_vals[name],
                                                      name)

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

        # Build IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestReadAll, self).tearDown()

    def testStructure(self):
        """Confirm structure of reading is as expected."""
        readings = self.ir_hub.read_all()
        assert type(readings) is dict, \
            "IR hub readings type: {}".format(type(reading))
        for name, reading in readings.iteritems():
            assert type(name) is str
            assert type(reading) is list
            for ir_value in reading:
                assert ir_value == 0


class TestReadCached(test_bot.TestBot):

    """Test reading IR arrays using a cache."""

    def setUp(self):
        """Get config and built IRHub object."""
        # Run general bot test setup
        super(TestReadCached, self).setUp()

        # Build IR hub abstraction object
        self.ir_hub = ir_hub_mod.IRHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestReadCached, self).tearDown()

    def testStructure(self):
        """Confirm structure of returned result is as expected."""
        result = self.ir_hub.read_cached()
        assert type(result) is dict, \
            "read_cached returned type: {}".format(type(result))

        # Validate IR reading data types
        assert type(result["readings"]) is dict
        for name, reading in result["readings"].iteritems():
            assert type(name) is str
            assert type(reading) is list
            for ir_value in reading:
                assert ir_value == 0

        # Validate time type
        assert type(result["time"]) is float

        # Validate freshness flag type
        assert type(result["fresh"]) is bool

    def testTime(self):
        """Test that time value is reasonable."""
        result = self.ir_hub.read_cached()
        # Just a very general assertion that the time's reasonable
        assert time() - result["time"] < 60

    def testSeries(self):
        """Test caching behavior with a series of reads over time."""
        max_staleness = .05
        # Do first read, which we expect to be fresh as there's no cache
        first_result = self.ir_hub.read_cached()
        assert first_result["fresh"] is True

        for delay in [0, .1]:
            sleep(delay)
            result = self.ir_hub.read_cached(max_staleness)
            if delay > .05:
                assert result["fresh"] is True
            else:
                assert result["fresh"] is False
