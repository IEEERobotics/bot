"""Test cases for wheel gunner."""
import sys
import os
import unittest
from random import randint

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
        """Setup test hardware files and build wheel gunner object."""
        # Load config
        config = lib.load_config()

        # Store original test flag and then set it to True
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # List of directories containing simulated hardware
        self.test_dirs = []

        # Collect simulated hardware test directories
        # TODO(dfarrell07): Remove magic nums by reading HW IDs from config
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
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

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
            for test_dir, motor in zip(self.test_dirs, self.wg.motors):
                with open(test_dir + '/duty_ns', 'r') as f:
                    # Duty is read like this by PWM getter
                    duty = int(f.read())
                    # Speed is derived this way in position getter
                    speed = int(round((duty / float(motor.pwm.period)) * 100))
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

        # List of directories containing simulated hardware
        self.test_dirs = []

        # Collect simulated hardware test directories
        # TODO(dfarrell07): Remove magic nums by reading HW IDs from config
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
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_fire(self):
        """Simply execute the fire method.

        TODO(dfarrell07): Flesh out this test.

        """
        self.wg.fire({"summary": "Test fire"})


class TestAdvanceDart(unittest.TestCase):

    """Test firing a dart.

    TODO(dfarrell07): Write test_manually_confirm test to check HW state.

    """

    def setUp(self):
        """Setup test hardware files and build wheel_gunner object."""
        # Load config
        config = lib.load_config()

        # Store original test flag and then set it to True
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # List of directories containing simulated hardware
        self.test_dirs = []

        # Collect simulated hardware test directories
        # TODO(dfarrell07): Remove magic nums by reading HW IDs from config
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
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_advance_dart(self):
        self.wg.advance_dart()
        assert self.wg.dart_sol.state == "retracted"
