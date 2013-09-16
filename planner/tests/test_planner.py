"""Test cases for planner."""
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
        self.wg_pwm_test_dirs = []
        for motor in self.config["gun_motors"]:
            # Collect PWM test dir
            pwm_test_dir = self.config["test_pwm_base_dir"] + str(motor["PWM"])
            self.wg_pwm_test_dirs.append(pwm_test_dir)

        # Collect simulated turret servo hardware test directories
        self.ts_test_dirs = {}
        for servo in self.config["turret_servos"]:
            test_dir = self.config["test_pwm_base_dir"] + str(servo["PWM"])
            self.ts_test_dirs[servo["axis"]] = test_dir

        # Collect simulated mec_driver motor hardware test directories
        self.md_pwm_test_dirs = {}
        self.md_gpio_test_dirs = {}
        for motor in self.config["drive_motors"]:
            # Collect PWM test dir
            pwm_test_dir = self.config["test_pwm_base_dir"] + str(motor["PWM"])
            self.md_pwm_test_dirs[motor["position"]] = pwm_test_dir

            # Collect GPIO test dir
            gpio_test_dir = self.config["test_gpio_base_dir"] +\
                                                        str(motor["GPIO"])
            self.md_gpio_test_dirs[motor["position"]] = gpio_test_dir

        # Collect simulated solenoid hardware test directory
        self.sol_test_dir = [self.config["test_gpio_base_dir"] +
                            str(self.config["gun_sol"]["GPIO"])]

        # Collect simulated GPIO hardware test directories
        gpio_test_dirs = self.sol_test_dir + self.md_gpio_test_dirs.values()

        # Collect simulated motor hardware test directories
        motr_test_dirs = self.wg_pwm_test_dirs + self.md_pwm_test_dirs.values()

        # Collect simulated servo hardware test directories
        servo_test_dirs = self.ts_test_dirs.values()

        # Set simulated servo PWM directories to known state
        for test_dir in servo_test_dirs:
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

        # Set simulated motor PWM directories to known state
        for test_dir in motr_test_dirs:
            # Create test directory if it doesn't exist
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

            # Set known values in all simulated hardware files
            with open(test_dir + "/run", "w") as f:
                f.write("0\n")
            with open(test_dir + "/duty_ns", "w") as f:
                f.write("250000\n")
            with open(test_dir + "/period_ns", "w") as f:
                f.write("1000000\n")
            with open(test_dir + "/polarity", "w") as f:
                f.write("0\n")

        # Set simulated GPIO directories to known state
        for test_dir in gpio_test_dirs:
            # Create test directory if it doesn't exist
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

            # Set known values in GPIO simulated hardware files
            with open(test_dir + "/value", "w") as f:
                f.write("0\n")
            with open(test_dir + "/direction", "w") as f:
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

    def test_follow_intersectionEx(self):
        """Test a follow action with an expected IntersectionException.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_follow_intersectionEx.yaml")
        p_mod.Planner()

    def test_follow_boxEx(self):
        """Test a follow action with an expected BoxException.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_follow_boxEx.yaml")
        p_mod.Planner()

    @unittest.expectedFailure
    def test_rote_move(self):
        """Test a rote move action.

        This test fails because mec_driver doesn't override driver's move
        method. The move method should accept a command string and handle it
        as a rote move or a command from follower.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_rote_move.yaml")
        p_mod.Planner()

    def test_fire(self):
        """Test a fire action.

        This test currently only checks that no exception is raised.

        TODO(dfarrell07): Find other ways to confirm correct behavior.

        """
        lib.set_strat("test_fire.yaml")
        p_mod.Planner()
