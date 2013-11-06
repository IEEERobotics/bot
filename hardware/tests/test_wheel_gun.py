"""Test cases for wheel_gun module."""

import sys
import os
import time
import unittest

try:
    import lib.lib as lib
    import tests.test_bot as test_bot
    import hardware.wheel_gun as wgun_mod
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise


class TestWheelGun(test_bot.TestBot):
    """Test wheel-based gun functions."""

    def setUp(self):
        """Setup test hardware files and create WheelGun instance"""
        # Run general bot test setup
        super(TestWheelGun, self).setUp()

        # Get logger
        self.logger = lib.get_logger()

        # Ensure simulated directories and files exist, and are reset
        self.setup_gpio(self.config['gun']['laser_gpio'])
        self.setup_gpio(self.config['gun']['motor_gpios']['left'])
        self.setup_gpio(self.config['gun']['motor_gpios']['right'])
        self.setup_gpio(self.config['gun']['trigger_gpios']['retract'])
        self.setup_gpio(self.config['gun']['trigger_gpios']['advance'])

        # Remap time.sleep to a dummy sleep function so that tests run fast
        real_sleep = time.sleep
        def dummy_sleep(duration):
            #print "[Dummy sleep: {} secs]".format(duration)  # [debug]
            real_sleep(0.001)  # call actual sleep, in case test depends on it
        time.sleep = dummy_sleep

        # Build WheelGun
        self.gun = wgun_mod.WheelGun()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestWheelGun, self).tearDown()

    def test_laser(self):
        """Test laser on-off function."""
        # Define a convenience function for checks used repeatedly
        def check_laser_gpio(value):
            assert int(self.get_gpio(
                self.config['gun']['laser_gpio'])['value']) == value

        # Test laser ON (1), should return 1
        state = self.gun.laser(1)
        assert state == 1, "Incorrect laser state: {}".format(state)
        check_laser_gpio(1)

        # Test laser OFF (0), should return 0
        state = self.gun.laser(0)
        assert state == 0, "Incorrect laser state: {}".format(state)
        check_laser_gpio(0)

        # Test invalid laser state (-1), should return None
        state = self.gun.laser(-1)
        assert state is None, "Incorrect laser state: {}".format(state)
        check_laser_gpio(0)

    def test_spin(self):
        """Test motor spinning function."""
        # Define a convenience function for checks used repeatedly
        def check_motor_gpios(value):
            assert int(self.get_gpio(
                self.config['gun']['motor_gpios']['left'])['value']) == value
            assert int(self.get_gpio(
                self.config['gun']['motor_gpios']['right'])['value']) == value

        # Test spin ON (1), should return 1
        state = self.gun.spin(1)
        assert state == 1, "Incorrect spin state: {}".format(state)
        check_motor_gpios(1)

        # Test spin OFF (0), should return 0
        state = self.gun.spin(0)
        assert state == 0, "Incorrect spin state: {}".format(state)
        check_motor_gpios(0)

        # Test invalid spin state (-1), should return None
        state = self.gun.spin(-1)
        assert state is None, "Incorrect spin state: {}".format(state)
        check_motor_gpios(0)

    def test_fire(self):
        """Test firing function."""
        # Define a convenience function for checks used repeatedly
        def check_trigger_gpios(value):
            assert int(self.get_gpio(
                self.config['gun']['trigger_gpios']['retract'])
                ['value']) == value
            assert int(self.get_gpio(
                self.config['gun']['trigger_gpios']['advance'])
                ['value']) == value

        # Test normal fire
        result = self.gun.fire()
        assert result is True
        check_trigger_gpios(0)

        # Test invalid trigger duration (negative)
        result = self.gun.fire(advance_duration=-0.5)
        assert result is False
        check_trigger_gpios(0)

        # Test excessive trigger duration (more than max)
        result = self.gun.fire(retract_duration=(
            float(self.config['gun']['max_trigger_duration']) + 1.0))
        assert result is True  # should still work with clamped duration
        check_trigger_gpios(0)

        # Test invalid delay (negative)
        result = self.gun.fire(delay=-3.0)
        assert result is False
        check_trigger_gpios(0)

    def test_fire_auto(self):
        """Test automatic-mode firing function."""
        # Test normal auto-fire
        result = self.gun.fire_auto()
        assert result is True
        # Test invalid count (negative)
        result = self.gun.fire_auto(count=-2)
        assert result is False
        # Test invalid delay (negative)
        result = self.gun.fire(delay=-1.0)
        assert result is False
