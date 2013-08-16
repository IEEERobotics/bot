"""Test cases for solenoid abstraction class."""
import sys
import os
import unittest
import random

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.solenoid as s_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestState(unittest.TestCase):
    """Test extending and retracting a solenoid"""

    def setUp(self):
        """Setup test hardware files and build solenoid object."""
        # ID number of solenoid
        self.s_num = 0

        # Load config
        config = lib.load_config()
        self.test_dir = config["test_gpio_base_dir"] + str(self.s_num)

        # Create test directory if it doesn't exist
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # Set known values in all simulated hardware files
        with open(self.test_dir + "/value", "w") as f:
            f.write("0\n")
        with open(self.test_dir + "/direction", "w") as f:
            f.write("out\n")

        # Build solenoid in testing mode
        self.solenoid = s_mod.Solenoid(self.s_num, testing=True)

    def test_extended(self):
        """Test extending solenoid."""
        self.solenoid.extend()
        assert self.solenoid.state == "extended"

    def test_retracted(self):
        """Test retracting solenoid."""
        self.solenoid.retract()
        assert self.solenoid.state == "retracted"

    def test_series(self):
        """Randomly extend and retract the solenoid."""
        for i in range(100):
            state = random.choice(["extended", "retracted"])
            if state == "extended":
                self.solenoid.extend()
                assert self.solenoid.state == "extended"
            else:
                self.solenoid.retract()
                assert self.solenoid.state == "retracted"

    def test_manually_confirm(self):
        """Test extending and retracting, read the simulated HW to confirm."""
        for i in range(100):
            state = random.choice(["extended", "retracted"])
            if state == "extended":
                self.solenoid.extend()
                with open(self.test_dir + '/value', 'r') as f:
                    assert int(f.read()) == 0
            else:
                self.solenoid.retract()
                with open(self.test_dir + '/value', 'r') as f:
                    assert int(f.read()) == 1


class TestDirection(unittest.TestCase):
    """Test the direction setting of the solenoid's GPIO pin."""

    def setUp(self):
        """Setup test hardware files and build solenoid object."""
        # ID number of solenoid
        self.s_num = 0

        # Load config
        config = lib.load_config()
        self.test_dir = config["test_gpio_base_dir"] + str(self.s_num)

        # Create test directory if it doesn't exist
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # Set known values in all simulated hardware files
        with open(self.test_dir + "/value", "w") as f:
            f.write("0\n")
        with open(self.test_dir + "/direction", "w") as f:
            f.write("out\n")

        # Build solenoid in testing mode
        self.solenoid = s_mod.Solenoid(self.s_num, testing=True)

    def test_direction(self):
        """Confirm that the solenoid's GPIO is set to output."""
        with open(self.test_dir + '/direction', 'r') as f:
            assert f.read() == "out\n"
