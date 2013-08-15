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
        """Build solenoid object."""
        self.s_mod = 0
        self.solenoid = s_mod.Solenoid(self.s_mod, testing=True)
        logger.debug("Built {}".format(self.solenoid))

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
        for i in range(25):
            state = random.choice(["extended", "retracted"])
            if state == "extended":
                self.solenoid.extend()
                assert self.solenoid.state == "extended"
            else:
                self.solenoid.retract()
                assert self.solenoid.state == "retracted"

    def test_manually_confirm(self):
        """Test extending and retracting, read the simulated HW to confirm."""
        config = lib.load_config()

        for i in range(10):
            state = random.choice(["extended", "retracted"])
            if state == "extended":
                self.solenoid.extend()
                with open(config["test_gpio_base_dir"] + str(self.s_mod) + 
                                                    '/value', 'r') as f:
                    assert int(f.read()) == 0
            else:
                self.solenoid.retract()
                with open(config["test_gpio_base_dir"] + str(self.s_mod) + 
                                                    '/value', 'r') as f:
                    assert int(f.read()) == 1

class TestDirection(unittest.TestCase):
    """Test the direction setting of the solenoid's GPIO pin."""

    def setUp(self):
        """Build solenoid object."""
        self.s_mod = 0
        self.solenoid = s_mod.Solenoid(self.s_mod, testing=True)
        logger.debug("Built {}".format(self.solenoid))

    def test_direction(self):
        """Confirm that the solenoid's GPIO is set to output."""
        config = lib.load_config()
        with open(config["test_gpio_base_dir"] + str(self.s_mod) + 
                                                 '/direction', 'r') as f:
            assert f.read() == "out\n"

