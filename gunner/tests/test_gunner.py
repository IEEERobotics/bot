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
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestAimTurret(unittest.TestCase):

    """Test changing the X and Y angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build gunner object."""
        # Load config
        config = lib.load_config()

        # Store original test flag and then set it to True
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Collect simulated hardware test directories
        self.test_dirs = {}
        for servo in config["turret_servos"]:
            test_dir = config["test_pwm_base_dir"] + str(servo["PWM"])
            self.test_dirs[servo["axis"]] = test_dir

        # Set simulated directories to known state
        for test_dir in self.test_dirs.values():
            # Create test directory if it doesn't exist
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

            # Set known values in all simulated hardware files
            with open(test_dir + "/run", "w") as f:
                f.write("1\n")
            with open(test_dir + "/duty_ns", "w") as f:
                f.write("15000000\n")
            with open(test_dir + "/period_ns", "w") as f:
                f.write("20000000\n")
            with open(test_dir + "/polarity", "w") as f:
                f.write("0\n")

        # Build wheel gunner
        self.gunner = g_mod.Gunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_series_xy(self):
        """Test a series of X and Y angles."""
        for angle in range(0, 180, 18):
            self.gunner.aim_turret(angle, angle)
            assert self.gunner.turret.x_angle == angle, "{} != {}".format(
                                                    self.gunner.turret.x_angle,
                                                    angle)
            assert self.gunner.turret.y_angle == angle

    def test_manually_confirm(self):
        """Test a series of random angles, read the simulated HW to confirm."""
        for i in range(10):
            test_x_angle = randint(0, 180)
            test_y_angle = randint(0, 180)
            self.gunner.aim_turret(test_x_angle, test_y_angle)
            with open(self.test_dirs["servo_x"] + '/duty_ns', 'r') as f:
                # Duty is read like this by PWM getter
                duty = int(f.read())
                # Angle is derived this way in angle getter
                read_angle = int(round(((duty - 10000000) / 10000000.) * 180))
                assert read_angle == test_x_angle, "{} != {}".format(
                                                    read_angle,
                                                    test_x_angle)
            self.gunner.y_angle = test_y_angle
            with open(self.test_dirs["servo_y"] + '/duty_ns', 'r') as f:
                # Duty is read like this by PWM getter
                duty = int(f.read())
                # Angle is derived this way in angle getter
                read_angle = int(round(((duty - 10000000) / 10000000.) * 180))
                assert read_angle == test_y_angle, "{} != {}".format(
                                                    read_angle,
                                                    test_y_angle)

    def test_x_over_max(self):
        """Test setting the X angle to greater than the max value."""
        self.gunner.aim_turret(181, 90)
        assert self.gunner.turret.x_angle == 180

    def test_x_under_min(self):
        """Test setting the X angle to less than the min value."""
        self.gunner.aim_turret(-1, 90)
        assert self.gunner.turret.x_angle == 0

    def test_y_over_max(self):
        """Test setting the Y angle to greater than the max value."""
        self.gunner.aim_turret(90, 181)
        assert self.gunner.turret.y_angle == 180

    def test_y_under_min(self):
        """Test setting the Y angle to less than the min value."""
        self.gunner.aim_turret(90, -1)
        assert self.gunner.turret.y_angle == 0


class TestFire(unittest.TestCase):

    """Test firing a dart.

    TODO(dfarrell07): Write test_manually_confirm test to check HW state.

    """

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        # Load config
        config = lib.load_config()

        # Store original test flag and then set it to True
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Collect simulated hardware test directories
        self.test_dirs = {}
        for servo in config["turret_servos"]:
            test_dir = config["test_pwm_base_dir"] + str(servo["PWM"])
            self.test_dirs[servo["axis"]] = test_dir

        # Set simulated directories to known state
        for test_dir in self.test_dirs.values():
            # Create test directory if it doesn't exist
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

            # Set known values in all simulated hardware files
            with open(test_dir + "/run", "w") as f:
                f.write("1\n")
            with open(test_dir + "/duty_ns", "w") as f:
                f.write("15000000\n")
            with open(test_dir + "/period_ns", "w") as f:
                f.write("20000000\n")
            with open(test_dir + "/polarity", "w") as f:
                f.write("0\n")

        # Build wheel gunner
        self.gunner = g_mod.Gunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_fire(self):
        """Simply execute the fire method.

        TODO(dfarrell07): Flesh out this test.

        """
        with self.assertRaises(NotImplementedError):
            self.gunner.fire()
