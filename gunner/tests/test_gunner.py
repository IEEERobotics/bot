"""Test cases for gunner."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import gunner.gunner as g_mod
    import hardware.turret as t_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestAimTurret(test_bot.TestBot):

    """Test changing the yaw and pitch angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build gunner object."""
        # Run general bot test setup
        super(TestAimTurret, self).setUp()

        # Build wheel gunner
        self.gunner = g_mod.Gunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAimTurret, self).tearDown()

    def test_series_yaw_pitch(self):
        """Test a series of yaw and pitch angles."""
        for angle in range(0, 180, 18):
            self.gunner.aim_turret(angle, angle)
            assert self.gunner.turret.yaw == angle, "{} != {}".format(
                                                    self.gunner.turret.yaw,
                                                    angle)
            assert self.gunner.turret.pitch == angle

    def test_manually_confirm(self):
        """Test a series of random angles, read the simulated HW to confirm."""
        for i in range(10):
            # Generate random yaw and pitch angles
            test_val = {}
            for servo in self.config["turret_servos"]:
                test_val[servo["axis"]] = randint(0, 180)

            # Set yaw and pitch angles
            self.gunner.aim_turret(test_val["yaw"], test_val["pitch"])

            # Check yaw and pitch angles
            for servo in self.config["turret_servos"]:
                duty = int(self.get_pwm(servo["PWM"])["duty_ns"])
                angle = int(round(((duty - 1000000) / 1000000.) * 180))
                assert test_val[servo["axis"]] == angle

    def test_yaw_over_max(self):
        """Test setting the yaw angle to greater than the max value."""
        with self.assertRaises(AssertionError):
            self.gunner.aim_turret(181, 90)

    def test_yaw_under_min(self):
        """Test setting the yaw angle to less than the min value."""
        with self.assertRaises(AssertionError):
            self.gunner.aim_turret(-1, 90)

    def test_pitch_over_max(self):
        """Test setting the pitch angle to greater than the max value."""
        with self.assertRaises(AssertionError):
            self.gunner.aim_turret(90, 181)

    def test_pitch_under_min(self):
        """Test setting the pitch angle to less than the min value."""
        with self.assertRaises(AssertionError):
            self.gunner.aim_turret(90, -1)


class TestFire(test_bot.TestBot):

    """Test firing a dart.

    TODO(dfarrell07): Write test_manually_confirm test to check HW state.

    """

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        # Run general bot test setup
        super(TestFire, self).setUp()

        # Build wheel gunner
        self.gunner = g_mod.Gunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestFire, self).tearDown()

    def test_fire(self):
        """Simply execute the fire method.

        TODO(dfarrell07): Flesh out this test.

        """
        with self.assertRaises(NotImplementedError):
            self.gunner.fire()
