"""Test cases for solenoid abstraction class."""

import unittest
import random

import lib.lib as lib
import hardware.solenoid as s_mod
import tests.test_bot as test_bot


@unittest.skip("No solenoids configured (not being used on bot)")
class TestState(test_bot.TestBot):

    """Test extending and retracting a solenoid"""

    def setUp(self):
        """Setup test hardware files and build solenoid object."""
        # Run general bot test setup
        super(TestState, self).setUp()

        # Get ID of solenoid, build solenoid in testing mode
        self.gpio_num = self.config["gun_sol"]["GPIO"]
        self.solenoid = s_mod.Solenoid(self.gpio_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestState, self).tearDown()

    def test_extended(self):
        """Test extending solenoid."""
        self.solenoid.extend()
        assert self.solenoid.state == "extended"

    def test_retracted(self):
        """Test retracting solenoid."""
        self.solenoid.retract()
        assert self.solenoid.state == "retracted"

    def test_series(self):
        """Randomly extend and retract the solenoid."""
        for i in range(10):
            state = random.choice(["extended", "retracted"])
            if state == "extended":
                self.solenoid.extend()
                assert self.solenoid.state == "extended"
            else:
                self.solenoid.retract()
                assert self.solenoid.state == "retracted"

    def test_manually_confirm(self):
        """Test extending and retracting, read the simulated HW to confirm."""
        for i in range(10):
            state = random.choice(["extended", "retracted"])
            if state == "extended":
                self.solenoid.extend()
                cur_gpio = self.get_gpio(self.gpio_num)
                assert int(cur_gpio["value"]) == 0
            else:
                self.solenoid.retract()
                cur_gpio = self.get_gpio(self.gpio_num)
                assert int(cur_gpio["value"]) == 1


@unittest.skip("No solenoids configured (not being used on bot)")
class TestDirection(test_bot.TestBot):

    """Test the direction setting of the solenoid's GPIO pin."""

    def setUp(self):
        """Setup test hardware files and build solenoid object."""
        # Run general bot test setup
        super(TestDirection, self).setUp()

        # Get ID of solenoid, build solenoid in testing mode
        self.gpio_num = self.config["gun_sol"]["GPIO"]
        self.solenoid = s_mod.Solenoid(self.gpio_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestDirection, self).tearDown()

    def test_direction(self):
        """Confirm that the solenoid's GPIO is set to output."""
        cur_gpio = self.get_gpio(self.gpio_num)
        assert cur_gpio["direction"] == "out\n"
