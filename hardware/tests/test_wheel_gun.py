"""Test cases for wheel_gun module."""

import sys
import os
import unittest

try:
    import lib.lib as lib
    import tests.test_bot as test_bot
    import hardware.wheel_gun as wg_mod
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

        # Build WheelGun
        self.gun = wg_mod.WheelGun()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestWheelGun, self).tearDown()

    def test_laser(self):
        """Test laser on-off function."""
        # Test laser ON (1), should return 1
        state = self.gun.laser(1)
        assert state == 1, "Incorrect laser state: {}".format(state)
        # Test laser OFF (0), should return 0
        state = self.gun.laser(0)
        assert state == 0, "Incorrect laser state: {}".format(state)
        # Test invalid laser state (-1), should return None
        state = self.gun.laser(-1)
        assert state is None, "Incorrect laser state: {}".format(state)

    def test_spin(self):
        """Test motor spinning function."""
        # Test spin ON (1), should return 1
        state = self.gun.spin(1)
        assert state == 1, "Incorrect spin state: {}".format(state)
        # Test spin OFF (0), should return 0
        state = self.gun.spin(0)
        assert state == 0, "Incorrect spin state: {}".format(state)
        # Test invalid spin state (-1), should return None
        state = self.gun.spin(-1)
        assert state is None, "Incorrect spin state: {}".format(state)

    def test_fire(self):
        """Test firing function."""
        # Test normal fire
        result = self.gun.fire()
        assert result is True
        # Test invalid trigger duration (negative)
        result = self.gun.fire(advance_duration=-0.5)
        assert result is False
        # Test excessive trigger duration (more than max)
        result = self.gun.fire(retract_duration=(
            float(self.config['gun']['max_trigger_duration']) + 1.0))
        assert result is True  # should still work with clamped duration
        # Test invalid delay (negative)
        result = self.gun.fire(delay=-3.0)
        assert result is False
