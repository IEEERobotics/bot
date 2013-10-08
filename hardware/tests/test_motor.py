"""Test cases for motor abstraction class."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.motor as m_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestSpeed(unittest.TestCase):

    """Test setting and checking the speed of a motor."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        # ID number of motor
        self.pwm_num = 0
        self.gpio_num = 0

        # Load config
        config = lib.load_config()
        self.pwm_test_dir = config["test_pwm_base_dir"] + str(self.pwm_num)
        self.gpio_test_dir = config["test_gpio_base_dir"] + str(self.gpio_num)

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Create test directories if they don't exist
        for test_dir in [self.pwm_test_dir, self.gpio_test_dir]:
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

        # Set known values in PWM simulated hardware files
        with open(self.pwm_test_dir + "/run", "w") as f:
            f.write("0\n")
        with open(self.pwm_test_dir + "/duty_ns", "w") as f:
            f.write("250000\n")
        with open(self.pwm_test_dir + "/period_ns", "w") as f:
            f.write("1000000\n")
        with open(self.pwm_test_dir + "/polarity", "w") as f:
            f.write("0\n")

        # Set known values in GPIO simulated hardware files
        with open(self.gpio_test_dir + "/value", "w") as f:
            f.write("0\n")
        with open(self.gpio_test_dir + "/direction", "w") as f:
            f.write("out\n")

        # Build motor in testing mode
        self.motor = m_mod.Motor(self.pwm_num, self.gpio_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_off(self):
        """Test turning the motor off."""
        self.motor.speed = 0
        assert self.motor.speed == 0

    def test_full(self):
        """Test turning the motor to 100% duty cycle."""
        self.motor.speed = 100
        assert self.motor.speed == 100

    def test_half(self):
        """Test the motor at half speed."""
        self.motor.speed = 50
        assert self.motor.speed == 50

    def test_accel(self):
        """Test a series of increasing speeds."""
        for speed in range(0, 100, 10):
            self.motor.speed = speed
            assert self.motor.speed == speed

    def test_manually_confirm(self):
        """Test a series of random speeds, read the simulated HW to confirm."""
        for i in range(10):
            test_speed = randint(0, 100)
            self.motor.speed = test_speed
            with open(self.pwm_test_dir + '/duty_ns', 'r') as f:
                # Duty is read like this by PWM getter
                duty = int(f.read())
                # Speed is derived this way in position getter
                speed = int(round((duty / float(self.motor.pwm.period)) * 100))
                assert speed == test_speed, "{} != {}".format(speed,
                                                              test_speed)

    def test_over_max(self):
        """Test speed over max speed. Should use maximum."""
        self.motor.speed = 101
        assert self.motor.speed == 100

    def test_under_min(self):
        """Test speed under minimum speed. Should use minimum."""
        self.motor.speed = -1
        assert self.motor.speed == 0


class TestDirection(unittest.TestCase):

    """Test setting and checking the direction of a motor."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        # ID number of motor
        self.pwm_num = 0
        self.gpio_num = 0

        # Load config
        config = lib.load_config()
        self.pwm_test_dir = config["test_pwm_base_dir"] + str(self.pwm_num)
        self.gpio_test_dir = config["test_gpio_base_dir"] + str(self.gpio_num)

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Create test directories if they don't exist
        for test_dir in [self.pwm_test_dir, self.gpio_test_dir]:
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

        # Set known values in PWM simulated hardware files
        with open(self.pwm_test_dir + "/run", "w") as f:
            f.write("0\n")
        with open(self.pwm_test_dir + "/duty_ns", "w") as f:
            f.write("250000\n")
        with open(self.pwm_test_dir + "/period_ns", "w") as f:
            f.write("1000000\n")
        with open(self.pwm_test_dir + "/polarity", "w") as f:
            f.write("0\n")

        # Set known values in GPIO simulated hardware files
        with open(self.gpio_test_dir + "/value", "w") as f:
            f.write("0\n")
        with open(self.gpio_test_dir + "/direction", "w") as f:
            f.write("out\n")

        # Build motor in testing mode
        self.motor = m_mod.Motor(self.pwm_num, self.gpio_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_forward(self):
        """Test motor in forward direction using text and int syntax."""
        self.motor.direction = m_mod.FORWARD
        assert self.motor.direction == "forward"
        self.motor.direction = "forward"
        assert self.motor.direction == "forward"

    def test_reverse(self):
        """Test motor in reverse direction using text and int syntax."""
        self.motor.direction = m_mod.REVERSE
        assert self.motor.direction == "reverse"
        self.motor.direction = "reverse"
        assert self.motor.direction == "reverse"

    def test_invalid(self):
        """Test a series of invalid directions."""
        # First set a valid value so state is known
        self.motor.direction = m_mod.FORWARD
        self.motor.direction = 2
        assert self.motor.direction == "forward"
        self.motor.direction = -1
        assert self.motor.direction == "forward"
        self.motor.direction = "wrong"
        assert self.motor.direction == "forward"
        self.motor.direction = ""
        assert self.motor.direction == "forward"


class TestNoDirection(unittest.TestCase):

    """Test a motor with no GPIO pin, and therefore no in-code direction."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        # ID number of motor
        self.pwm_num = 0
        self.gpio_num = 0

        # Load config
        config = lib.load_config()
        self.pwm_test_dir = config["test_pwm_base_dir"] + str(self.pwm_num)

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Create test directories if they don't exist
        for test_dir in [self.pwm_test_dir]:
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

        # Set known values in PWM simulated hardware files
        with open(self.pwm_test_dir + "/run", "w") as f:
            f.write("0\n")
        with open(self.pwm_test_dir + "/duty_ns", "w") as f:
            f.write("250000\n")
        with open(self.pwm_test_dir + "/period_ns", "w") as f:
            f.write("1000000\n")
        with open(self.pwm_test_dir + "/polarity", "w") as f:
            f.write("0\n")

        # Build motor in testing mode
        self.motor = m_mod.Motor(self.pwm_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_set_dir(self):
        """Test setting a direction for a motor that should have no direction.

        As there should be no result from this call, we're just checking that
        no exception is raised.

        """
        self.motor.direction = m_mod.FORWARD
        self.motor.direction = "forward"
        self.motor.direction = "reverse"

    def test_get_dir(self):
        """Get direction for a motor that should have no direction."""
        assert self.motor.direction == None

    def test_vol(self):
        """Get velocity for a motor that has no direction."""
        assert self.motor.velocity == self.motor.speed
        self.motor.speed = 50
        assert self.motor.speed == 50
        assert self.motor.velocity == 50
