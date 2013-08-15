#!/usr/bin/env python
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
        """Build motor object."""
        self.m_num = 0
        self.motor = m_mod.Motor(self.m_num, testing=True)
        logger.debug("Built {}".format(self.motor))

    def test_off(self):
        """Test turning the motor off."""
        self.motor.speed = 0
        assert self.motor.speed is 0

    def test_full(self):
        """Test turning the motor to 100% duty cycle."""
        self.motor.speed = 100
        assert self.motor.speed is 100

    def test_half(self):
        """Test the motor at half speed."""
        self.motor.speed = 50
        assert self.motor.speed is 50

    def test_accel(self):
        """Test a series of increasing speeds."""
        for speed in range (0, 100, 5):
            self.motor.speed = speed
            assert self.motor.speed is speed

    def test_manually_confirm(self):
        """Test a series of random speeds, read the simulated HW to confirm."""
        config = lib.load_config()

        for i in range(10):
            cur_speed = randint(0, 100)
            self.motor.speed = cur_speed
            with open(config["test_base_dir"] + str(self.m_num) + 
                                                '/duty_ns', 'r') as f:
                assert int(f.read()) is cur_speed

    def test_over_max(self):
        """Test speed over max speed. Should use maximum."""
        self.motor.speed = 101
        assert self.motor.speed is 100

    def test_under_min(self):
        """Test speed under minimum speed. Should use minimum."""
        self.motor.speed = -1
        assert self.motor.speed is 0


class TestDirection(unittest.TestCase):
    """Test setting and checking the direction of a motor."""

    def setUp(self):
        """Build motor object."""
        self.m_num = 0
        self.motor = m_mod.Motor(self.m_num, testing=True)
        logger.debug("Built {}".format(self.motor))

    def test_forward(self):
        """Test motor in foward direction using text and int syntax."""
        self.motor.direction = 1
        assert self.motor.direction is 1
        self.motor.direction = "foward"
        assert self.motor.direction is 1

    def test_reverse(self):
        """Test motor in reverse direction using text and int syntax."""
        self.motor.direction = 0
        assert self.motor.direction is 0
        self.motor.direction = "reverse"
        assert self.motor.direction is 0

    def test_invalid(self):
        """Test a series of invalid directions."""
        # First set a valid value so state is known
        self.motor.direction = 1
        self.motor.direction = 2
        assert self.motor.direction is 1
        self.motor.direction = -1
        assert self.motor.direction is 1
        self.motor.direction = "wrong"
        assert self.motor.direction is 1
        self.motor.direction = ""
        assert self.motor.direction is 1
