"""Test cases for turret abstraction class."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.turret as t_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestAngle(unittest.TestCase):

    """Test setting and checking the X and Y angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build turret object."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # List of directories containing simulated hardware
        self.test_dirs = []

        # Collect simulated hardware test directories
        self.test_dirs = {
            "dir_x": config["test_pwm_base_dir"] + str(t_mod.SERVO_X_ID),
            "dir_y": config["test_pwm_base_dir"] + str(t_mod.SERVO_Y_ID)
            }

        # Set simulated directories to known state
        for test_dir in self.test_dirs.values():
            # Create test directory if it doesn't exist
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

            # Set known values in all simulated hardware files
            with open(test_dir + "/run", "w") as f:
                f.write("0\n")
            with open(test_dir + "/duty_ns", "w") as f:
                f.write("0\n")
            with open(test_dir + "/period_ns", "w") as f:
                f.write("1000\n")
            with open(test_dir + "/polarity", "w") as f:
                f.write("0\n")

        # Build turret in testing mode
        self.turret = t_mod.Turret()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

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
            test_x_angle = randint(0, 180)
            self.turret.x_angle = test_x_angle
            with open(self.test_dirs["dir_x"] + '/duty_ns', 'r') as f:
                # Duty is read like this by PWM getter
                duty = int(f.read())
                # Angle is derived this way in angle getter
                read_angle = int(round(((duty - 1000) / 1000.) * 180))
                assert read_angle == test_x_angle, "{} != {}".format(
                                                    read_angle,
                                                    test_x_angle)
            test_y_angle = randint(0, 180)
            self.turret.y_angle = test_y_angle
            with open(self.test_dirs["dir_y"] + '/duty_ns', 'r') as f:
                # Duty is read like this by PWM getter
                duty = int(f.read())
                # Angle is derived this way in angle getter
                read_angle = int(round(((duty - 1000) / 1000.) * 180))
                assert read_angle == test_y_angle, "{} != {}".format(
                                                    read_angle,
                                                    test_y_angle)

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
