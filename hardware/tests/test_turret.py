"""Test cases for turret abstraction class."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.turret as t_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestAngle(test_bot.TestBot):

    """Test setting and checking the X and Y angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build turret object."""
        # Run general bot test setup
        super(TestAngle, self).setUp()

        # Build turret in testing mode
        self.turret = t_mod.Turret()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAngle, self).tearDown()

    def test_x_0(self):
        """Test setting the X angle to min value."""
        self.turret.x_angle = 0
        assert self.turret.x_angle == 0

    def test_x_180(self):
        """Test setting the X angle to max value."""
        self.turret.x_angle = 180
        assert self.turret.x_angle == 180

    def test_x_90(self):
        """Test setting the X angle to middle value."""
        self.turret.x_angle = 90
        assert self.turret.x_angle == 90

    def test_y_0(self):
        """Test setting the Y angle to min value."""
        self.turret.y_angle = 0
        assert self.turret.y_angle == 0

    def test_y_180(self):
        """Test setting the Y angle to max value."""
        self.turret.y_angle = 180
        assert self.turret.y_angle == 180

    def test_y_90(self):
        """Test setting the Y angle to middle value."""
        self.turret.y_angle = 90
        assert self.turret.y_angle == 90

    def test_series_x(self):
        """Test a series of X angles."""
        for angle in range(0, 180, 18):
            self.turret.x_angle = angle
            assert self.turret.x_angle == angle

    def test_series_y(self):
        """Test a series of Y angles."""
        for angle in range(0, 180, 18):
            self.turret.y_angle = angle
            assert self.turret.y_angle == angle

    def test_series_xy(self):
        """Test a series of X and Y angles."""
        for angle in range(0, 180, 18):
            self.turret.x_angle = angle
            self.turret.y_angle = angle
            assert self.turret.x_angle == angle
            assert self.turret.y_angle == angle

    def test_manually_confirm(self):
        """Test a series of random angles, read the simulated HW to confirm."""
        for i in range(10):
            # Generate random x and y angles
            test_val = {}
            for servo in self.config["turret_servos"]:
                test_val[servo["axis"]] = randint(0, 180)

            # Set x and y angles
            self.turret.x_angle = test_val["servo_x"]
            self.turret.y_angle = test_val["servo_y"]

            # Check x and y angles
            for servo in self.config["turret_servos"]:
                duty = int(self.get_pwm(servo["PWM"])["duty_ns"])
                angle = int(round(((duty - 1000000) / 1000000.) * 180))
                assert test_val[servo["axis"]] == angle

    def test_x_over_max(self):
        """Test setting the X angle to greater than the max value."""
        self.turret.x_angle = 181
        assert self.turret.x_angle == 180

    def test_x_under_min(self):
        """Test setting the X angle to less than the min value."""
        self.turret.x_angle = -1
        assert self.turret.x_angle == 0

    def test_y_over_max(self):
        """Test setting the Y angle to greater than the max value."""
        self.turret.y_angle = 181
        assert self.turret.y_angle == 180

    def test_y_under_min(self):
        """Test setting the Y angle to less than the min value."""
        self.turret.y_angle = -1
        assert self.turret.y_angle == 0
