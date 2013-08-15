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
        """Build servo object."""
        # ID number of servo
        self.s_num = 0

        # Load config
        self.config = lib.load_config()
        self.test_dir = self.config["test_pwm_base_dir"] + str(self.s_num)

        # Create test directory if it doesn't exist
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # Set known values in all simulated hardware files
        with open(self.test_dir + "/run", "w") as f:
            f.write("0\n")
        with open(self.test_dir + "/duty_ns", "w") as f:
            f.write("0\n")
        with open(self.test_dir + "/period_ns", "w") as f:
            f.write("1000\n")
        with open(self.test_dir + "/polarity", "w") as f:
            f.write("0\n")

        # Build servo in testing mode
        self.servo = s_mod.Servo(self.s_num, testing=True)
        logger.debug("Built {}".format(self.servo))

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

    @unittest.expectedFailure
    def test_manually_confirm(self):
        """Test a series of random positions, read simulated HW to confirm."""
        for i in range(1000):
            cur_position = randint(0, 100)
            logger.debug("Testing position {}".format(cur_position))
            self.servo.position = cur_position
            with open(self.test_dir + "/duty_ns", "r") as f:
                duty = int(f.read())
                read_position = int(((duty - 1000) / 1000.) * 100)
                logger.debug("Read position: {}".format(read_position))
                assert read_position == cur_position, "{} != {}".format(
                                                        read_position,
                                                        cur_position)

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
