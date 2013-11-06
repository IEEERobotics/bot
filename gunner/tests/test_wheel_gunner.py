"""Test cases for wheel gunner."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import gunner.wheel_gunner as wg_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestUpdateRotateSpeed(test_bot.TestBot):

    """Test updating wheel rotation speed."""

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        # Run general bot test setup
        super(TestUpdateRotateSpeed, self).setUp()

        # Build wheel gunner
        self.wg = wg_mod.WheelGunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestUpdateRotateSpeed, self).tearDown()

    def test_off(self):
        """Test zero wheel rotation."""
        self.wg.wheel_speed = 0
        assert self.wg.wheel_speed == 0

    def test_full(self):
        """Test turning the wheels to 100% duty cycle."""
        self.wg.wheel_speed = 100
        assert self.wg.wheel_speed == 100

    def test_half(self):
        """Test the wheels at half speed."""
        self.wg.wheel_speed = 50
        assert self.wg.wheel_speed == 50

    def test_accel(self):
        """Test a series of increasing speeds."""
        for speed in range(0, 100, 10):
            self.wg.wheel_speed = speed
            assert self.wg.wheel_speed == speed

    def test_manually_confirm(self):
        """Test a series of random speeds, read the simulated HW to confirm."""
        for i in range(10):
            test_speed = randint(0, 100)
            self.wg.wheel_speed = test_speed

            for motor in self.config["gun_motors"]:
                cur_pwm = self.get_pwm(motor["PWM"])
                duty = int(cur_pwm["duty_ns"])
                period = int(cur_pwm["period_ns"])
                speed = int(round((duty / float(period)) * 100))
                assert speed == test_speed, "{} != {}".format(speed, 
                                                              test_speed)

    def test_over_max(self):
        """Test speed over max speed. Should use maximum."""
        with self.assertRaises(AssertionError):
            self.wg.wheel_speed = 101

    def test_under_min(self):
        """Test speed under minimum speed. Should use minimum."""
        with self.assertRaises(AssertionError):
            self.wg.wheel_speed = -1


class TestAutoFire(test_bot.TestBot):

    """Test firing a dart.

    TODO(dfarrell07): Write test_manually_confirm test to check HW state.

    """

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        # Run general bot test setup
        super(TestAutoFire, self).setUp()

        # Build wheel gunner
        self.wg = wg_mod.WheelGunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAutoFire, self).tearDown()

    def test_auto_fire(self):
        """Simply execute the fire method.

        TODO(dfarrell07): Flesh out this test.

        """
        self.wg.auto_fire()


class TestAdvanceDart(test_bot.TestBot):

    """Test firing a dart.

    TODO(dfarrell07): Write test_manually_confirm test to check HW state.

    """

    def setUp(self):
        """Setup test hardware files and build wheel_gunner object."""
        # Run general bot test setup
        super(TestAdvanceDart, self).setUp()

        # Build wheel gunner
        self.wg = wg_mod.WheelGunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAdvanceDart, self).tearDown()

    def test_advance_dart(self):
        self.wg.advance_dart()
        assert self.wg.gun_sol.state == "retracted"
