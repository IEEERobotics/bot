"""Test cases for servo abstraction class."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.servo as s_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestPosition(unittest.TestCase):
    """Test setting and checking the position of a servo."""

    def setUp(self):
        """Setup test hardware files and build servo object."""
        # ID number of servo
        self.s_num = 0

        # Load config
        config = lib.load_config()
        self.test_dir = config["test_pwm_base_dir"] + str(self.s_num)

        # Set testing flag in config
        lib.set_testing(True)

        # Create test directory if it doesn't exist
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # Set known values in all simulated hardware files
        with open(self.test_dir + "/run", "w") as f:
            f.write("0\n")
        with open(self.test_dir + "/duty_ns", "w") as f:
            f.write("1500\n")
        with open(self.test_dir + "/period_ns", "w") as f:
            f.write("20000\n")
        with open(self.test_dir + "/polarity", "w") as f:
            f.write("0\n")

        # Build servo in testing mode
        self.servo = s_mod.Servo(self.s_num)

    def tearDown(self):
        # Reset testing flag in config to False
        lib.set_testing(False)

    def test_0(self):
        """Test setting servo position to max in zero direction."""
        self.servo.position = 0
        assert self.servo.position == 0, self.servo.position

    def test_100(self):
        """Test setting servo position to max in 100 direction."""
        self.servo.position = 100
        assert self.servo.position == 100, self.servo.position

    def test_middle(self):
        """Test the servo at middle position."""
        self.servo.position = 50
        assert self.servo.position == 50, self.servo.position

    def test_series(self):
        """Test a series of positions."""
        for position in range(0, 100, 5):
            self.servo.position = position
            assert self.servo.position == position, self.servo.position

    def test_manually_confirm(self):
        """Test a series of random positions, read simulated HW to confirm."""
        for i in range(100):
            test_position = randint(0, 100)
            self.servo.position = test_position
            with open(self.test_dir + "/duty_ns", "r") as f:
                # Duty is read like this by PWM getter
                duty = int(f.read())
                # Position is derived this way in position getter
                read_position = int(round(((duty - 1000) / 1000.) * 100))
                assert read_position == test_position, "{} != {}".format(
                                                        read_position,
                                                        test_position)

    def test_over_max(self):
        """Test position over max position. Should use maximum."""
        self.servo.position = 101
        assert self.servo.position == 100, \
                                      "Actual: {}".format(self.servo.position)

    def test_under_min(self):
        """Test position under minimum position. Should use minimum."""
        self.servo.position = -1
        assert self.servo.position == 0, \
                                      "Actual: {}".format(self.servo.position)
