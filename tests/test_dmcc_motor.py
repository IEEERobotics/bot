"""Test cases for DMCC motor abstraction class."""

from os import path
from unittest import TestCase, expectedFailure

import pyDMCC

import tests.test_bot as test_bot
from bot.hardware.dmcc_motor import DMCCMotorSet, DMCCMotor
import bot.lib.lib as lib


class TestDMCCMotorSet(TestCase):

    """Test motor set."""

    def setUp(self):
        config = path.dirname(path.realpath(__file__))+"/test_config.yaml"
        self.config = lib.get_config(config)
        self.logger = lib.get_logger()
        self.logger.info("Running {}()".format(self._testMethodName))

    def test_instantiate(self):
        conf = {'a_motor': {'board_num': 0, 'motor_num': 1}}
        motor_set = DMCCMotorSet(conf)
        self.assertIsInstance(motor_set['a_motor'], DMCCMotor)

    def test_multiple_config(self):
        drive_conf = self.config['dmcc_drive_motors']
        drive_motor_set = DMCCMotorSet(drive_conf)
        self.assertEqual(len(drive_motor_set.motors), 4)

    def test_bad_config(self):
        motor_conf = self.config['dmcc_bad_motor_def']
        with self.assertRaises(KeyError):
            drive_motor_set = DMCCMotorSet(motor_conf)


class TestDMCCMotor(TestCase):

    """Test motor functions."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        config = path.dirname(path.realpath(__file__))+"/test_config.yaml"
        self.config = lib.get_config(config)
        self.logger = lib.get_logger()
        self.logger.info("Running {}()".format(self._testMethodName))
        motor_conf = self.config['dmcc_drive_motors']
        self.motor_set = DMCCMotorSet(motor_conf)

    def test_instantiate(self):
        motor = self.motor_set['front_left']
        self.assertIsInstance(motor, DMCCMotor)
        self.assertIsInstance(motor.real_motor, pyDMCC.Motor)

    def test_set_power(self):
        """Test setting the motor power"""
        motor = self.motor_set['front_left']
        motor.power = 0
        assert motor.power == 0
        motor.power = 50
        assert motor.power == 50

    def test_power_invert(self):
        """Test the effect of setting inverted power mode"""
        motor_conf = self.config['dmcc_inverted']
        motor_set = DMCCMotorSet(motor_conf)
        normal = motor_set['normal_motor']
        inverted = motor_set['inverted_motor']
        normal.power = 25
        self.assertEqual(normal._power, 25)
        inverted.power = 25
        self.assertEqual(inverted._power, -25)

    def test_set_velocity_no_PID(self):
        """Test setting the motor velocity"""
        with self.assertRaises(RuntimeError):
            self.motor_set['front_left'].velocity = 0

    def test_set_velocity(self):
        """Test setting the motor velocity"""
        motor = self.motor_set['front_left']
        motor.setVelocityPID(1000, 100, 10)
        motor.velocity = 0
        assert motor.velocity == 0
        motor.velocity = 50
        assert motor.velocity == 50

    @expectedFailure
    def test_get_voltage(self):
        """Test getting the supply voltage for a motor"""
        print self.dmcc_motor.dmcc.i2c
        assert self.dmcc_motor.voltage == 0

#    def test_position_PID(self):
#        """Test setting PID constants to control position."""
#        assert self.motor.setPositionPID(-5000, -100, -500)
#        target_position = 5000
#        self.motor.position = target_position
#        self.logger.debug("[PID] position: {}".format(self.motor.position))
#        assert self.motor.position == target_position
#        self.motor.position = 0  # set back to zero
#
#    def test_velocity_PID(self):
#        """Test setting PID constants to control velocity."""
#        assert self.motor.setVelocityPID(-5000, -100, -500)
#        target_velocity = 1000
#        self.motor.velocity = target_velocity
#        self.logger.debug("[PID] velocity: {}".format(self.motor.velocity))
#        assert self.motor.velocity == target_velocity
#        self.motor.velocity = 0  # set back to zero
