"""Test cases wheel gunner."""
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import gunner.wheel_gunner as wg_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestUpdateRotateSpeed(unittest.TestCase):
    """Test updating wheel rotation speed."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        lib.set_testing(True)

        # List of directories containing simulated hardware
        self.test_dirs = []

        # Collect simulated hardware test directories
        for m_num in range(0, 2):
            self.test_dirs.append(config["test_pwm_base_dir"] + str(m_num))

        # Set simulated directories to known state
        for test_dir in self.test_dirs:
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

        # Build wheel gunner
        self.wg = wg_mod.WheelGunner()

    def tearDown(self):
        # Reset testing flag in config to False
        lib.set_testing(False)

    def test_off(self):
        """Test zero wheel rotation."""
        self.wg.wheel_speed = 0
        assert self.wg.wheel_speed == 0

    def test_full(self):
        """Test turning the motor to 100% duty cycle."""
        self.wg.wheel_speed = 100
        assert self.wg.wheel_speed == 100

    def test_half(self):
        """Test the motor at half speed."""
        self.wg.wheel_speed = 50
        assert self.wg.wheel_speed == 50

    def test_accel(self):
        """Test a series of increasing speeds."""
        for speed in range(0, 100, 5):
            self.wg.wheel_speed = speed
            assert self.wg.wheel_speed == speed

    @unittest.skip("Not complete")
    def test_manually_confirm(self):
        """Test a series of random speeds, read the simulated HW to confirm."""
        for i in range(100):
            test_speed = randint(0, 100)
            self.wg.wheel_speed = test_speed
            with open(self.test_dir + '/duty_ns', 'r') as f:
                # Duty is read like this by PWM getter
                duty = int(f.read())
                # Speed is derived this way in position getter
                speed = int(round((duty / float(self.motor.pwm.period)) * 100))
                assert speed == test_speed, "{} != {}".format(speed,
                                                              test_speed)

    def test_over_max(self):
        """Test speed over max speed. Should use maximum."""
        self.wg.wheel_speed = 101
        assert self.wg.wheel_speed == 100

    def test_under_min(self):
        """Test speed under minimum speed. Should use minimum."""
        self.wg.wheel_speed = -1
        assert self.wg.wheel_speed == 0

@unittest.skip("Not complete")
class TestDirection(unittest.TestCase):
    """Test setting and checking the direction of a motor."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        # ID number of motor
        self.m_num = 0

        # Load config
        config = lib.load_config()
        self.test_dir = config["test_pwm_base_dir"] + str(self.m_num)

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

        # Build motor in testing mode
        self.motor = m_mod.Motor(self.m_num, testing=True)

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
