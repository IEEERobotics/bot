"""Test cases planner."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import planner.planner as p_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestExecStrategy(unittest.TestCase):

    """Test executing strategies."""

    def setUp(self):
        """Setup test hardware files and build planner object."""
        # Store original test flag and then set it to True
        self.config = lib.load_config()
        self.orig_test_state = self.config["testing"]
        self.orig_strat_file = self.config["strategy"]
        lib.set_testing(True)

        # Collect simulated wheel_gunner hardware test directories
        self.wg_test_dirs = []
        for motor in self.config["gun_motors"]:
            test_dir = self.config["test_pwm_base_dir"] + str(motor["PWM"])
            self.wg_test_dirs.append(test_dir)

        # Collect simulated turret servo hardware test directories
        self.ts_test_dirs = {}
        for servo in self.config["turret_servos"]:
            test_dir = self.config["test_pwm_base_dir"] + str(servo["PWM"])
            self.ts_test_dirs[servo["axis"]] = test_dir

        # Collect simulated mech_driver motor hardware test directories
        self.md_test_dirs = {}
        for motor in self.config["drive_motors"]:
            test_dir = self.config["test_pwm_base_dir"] + str(motor["PWM"])
            self.md_test_dirs[motor["position"]] = test_dir

        # Collect simulated solenoid hardware test directory
        self.sol_test_dir = self.config["test_gpio_base_dir"] +\
                            str(self.config["gun_sol"]["GPIO"])

        # Set simulated PWM directories to known state
        pwm_test_dirs = self.wg_test_dirs + self.ts_test_dirs.values() +\
                                            self.md_test_dirs.values()
        for test_dir in pwm_test_dirs:
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

        # Set known values in solenoid GPIO simulated hardware files
        with open(self.sol_test_dir + "/value", "w") as f:
            f.write("0\n")
        with open(self.sol_test_dir + "/direction", "w") as f:
            f.write("out\n")

    def tearDown(self):
        """Restore testing flag state and strategy in config file."""
        lib.set_testing(self.orig_test_state)
        lib.set_strat_qual(self.orig_strat_file)

    def test_empty(self):
        """Test planner's handling of an empty strategy file."""
        lib.set_strat("test_empty.yaml")
        with self.assertRaises(AssertionError):
            p_mod.Planner()
