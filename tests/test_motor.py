"""Test cases for motor abstraction class."""

from random import randint
from unittest import TestCase
from os import path

import bot.lib.lib as lib
import bot.hardware.motor as m_mod
from tests.test_bot import TestBot


class TestSpeed(TestBot):

    """Test setting and checking the speed of a motor."""

    def setUp(self):
        """Setup test hardware files and build motor object."""

        config = path.dirname(path.realpath(__file__))+"/test_config.yaml"
        self.config = lib.get_config(config)

        # Build motor in testing mode
        self.pwm_num = self.config["two_motors"][0]["PWM"]
        self.gpio_num = self.config["two_motors"][0]["GPIO"]
        self.setup_pwm(self.pwm_num, "1\n", "0\n", "1000\n", "0\n")
        self.setup_gpio(self.gpio_num)
        self.motor = m_mod.Motor(self.pwm_num, self.gpio_num)

    def tearDown(self):
        pass

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
            # Generate random speed and set motor to that speed
            test_speed = randint(0, 100)
            self.motor.speed = test_speed

            # Confirm that motor was set correctly
            cur_pwm = self.get_pwm(self.pwm_num)
            duty = int(cur_pwm["duty_ns"])
            period = int(cur_pwm["period_ns"])
            speed = int(round((duty / float(period)) * 100))
            assert speed == test_speed, "{} != {}".format(speed, test_speed)

    def test_over_max(self):
        """Test speed over max speed. Should use maximum."""
        self.motor.speed = 101
        assert self.motor.speed == 100

    def test_under_min(self):
        """Test speed under minimum speed. Should use minimum."""
        self.motor.speed = -1
        assert self.motor.speed == 0


class TestDirection(TestBot):

    """Test setting and checking the direction of a motor."""

    def setUp(self):
        """Setup test hardware files and build motor object."""

        config = path.dirname(path.realpath(__file__))+"/test_config.yaml"
        self.config = lib.get_config(config)

        # Build motor in testing mode
        self.pwm_num = self.config["two_motors"][0]["PWM"]
        self.gpio_num = self.config["two_motors"][0]["GPIO"]
        self.setup_pwm(self.pwm_num, "1\n", "0\n", "1000\n", "0\n")
        self.setup_gpio(self.gpio_num)
        self.motor = m_mod.Motor(self.pwm_num, self.gpio_num)

    def tearDown(self):
        pass

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


class TestNoDirection(TestCase):

    """Test a motor with no GPIO pin, and therefore no in-code direction."""

    def setUp(self):
        """Setup test hardware files and build motor object."""

        config = path.dirname(path.realpath(__file__))+"/test_config.yaml"
        self.config = lib.get_config(config)

        # Build motor in testing mode
        self.pwm_num = self.config["two_motors"][0]["PWM"]
        self.motor = m_mod.Motor(self.pwm_num)

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
        assert self.motor.direction is None

    def test_vol(self):
        """Get velocity for a motor that has no direction."""
        assert self.motor.velocity == self.motor.speed
        self.motor.speed = 50
        assert self.motor.speed == 50
        assert self.motor.velocity == 50
