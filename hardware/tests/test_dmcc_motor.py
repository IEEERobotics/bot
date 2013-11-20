"""Test cases for DMCC motor abstraction class."""

import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.dmcc_motor as dm_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()  # TODO: TestBot should have a logger member


class TestDMCCMotor(test_bot.TestBot):

    """Test motor functions."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        # Run general bot test setup
        super(TestDMCCMotor, self).setUp()

        # Build motor in testing mode (TODO: Update config.yaml and use that)
        self.board_num = 0  # self.config["drive_motors"][0]["board"]
        self.motor_num = 1  # self.config["drive_motors"][0]["motor"]
        self.motor = dm_mod.DMCCMotor(self.board_num, self.motor_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestDMCCMotor, self).tearDown()

    def test_stop(self):
        """Test stopping the motor."""
        self.motor.power = 0
        assert self.motor.power == 0

    def test_power_limits(self):
        """Test setting the motor's power to min, max, under, over."""
        logger.info("[init] motor power: {}".format(self.motor.power))

        # Min
        self.motor.power = dm_mod.DMCCMotor.power_range.min
        logger.info("[min] motor power: {}".format(self.motor.power))
        assert self.motor.power == dm_mod.DMCCMotor.power_range.min

        # Max
        self.motor.power = dm_mod.DMCCMotor.power_range.max
        logger.info("[max] motor power: {}".format(self.motor.power))
        assert self.motor.power == dm_mod.DMCCMotor.power_range.max

        # Under min; should use min
        self.motor.power = dm_mod.DMCCMotor.power_range.min - 1
        logger.info("[under] motor power: {}".format(self.motor.power))
        assert self.motor.power == dm_mod.DMCCMotor.power_range.min

        # Over max; should use max
        self.motor.power = dm_mod.DMCCMotor.power_range.max + 1
        logger.info("[over] motor power: {}".format(self.motor.power))
        assert self.motor.power == dm_mod.DMCCMotor.power_range.max

    def test_power_sweep(self):
        """Test a series of increasing power values from min to max."""
        power_step = (dm_mod.DMCCMotor.power_range.max -
            dm_mod.DMCCMotor.power_range.min) / 20
        for power in range(dm_mod.DMCCMotor.power_range.min,
                dm_mod.DMCCMotor.power_range.max, power_step):
            self.motor.power = power
            assert self.motor.power == power

    # TODO: Test velocity
