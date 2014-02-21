"""Abstraction layer for DMCC-based motors."""

import lib.lib as lib
import pyDMCC
from collections import defaultdict

class DMCCMotorSet(object):
    """A single interface to a collection of DMCCs and associated motors."""

    def __init__(self, motor_config):
        """Initialize a set of DMCCs and their associated motors

        :param motor_config: Config entry mapping motor names to DMCC ids and motor indices

        Dictionary entries are in the format:
            <motor_name>: { board_num: [0-3], motor_num: [1-2] }

        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()
        self.is_testing = self.config["testing"]

        #print "Testing: ", self.config["testing"]
        #print pyDMCC.lib._config

        # This instantiates all DMCCs in every DMCCManager, which is probably
        # not optimal, which works fine for our purposes.  Potentially better
        # approaches:
        #  - global state: shared dmccs dictionary, instantiated once
        #  - selected instantiation: only initialize the dmccs we are control
        if not self.is_testing:
            dmccs = pyDMCC.autodetect()
            self.logger.debug("Found %d physical DMCC boards" % len(dmccs))
        else:
            self.logger.debug("Skipping autodetect due to test mode")
            dmccs = defaultdict(lambda: pyDMCC.DMCC(0, verify=False, bus=None))

        self.motors = {}
        for name,conf in motor_config.items():
            try:
                self.motors[name] = DMCCMotor( dmccs[conf['board_num']], conf['motor_num'] )
            except KeyError:
                self.logger.error("Bad motor definition for motor: '{}'".format(name))
                raise KeyError

        self.logger.debug("Setup {}".format(self))

    def __getitem__(self, index):
        return self.motors[index]

    def __str__(self):
        return "{} for motors: {}".format(self.__class__.__name__, self.motors.keys())


class DMCCMotor(object):

    def __init__(self, dmcc, motor_num):
        """Wraps an individual pyDMCC motor

        :param dmcc: Controlling dmcc, None when testing
        :param motor_num: Motor number in motor_num_range.
        :type motor_num: int

        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.is_testing = self.config["testing"]

        self.dmcc = dmcc
        self.real_motor = dmcc.motors[motor_num]
        self.motor_num = motor_num

        self._power = 0  # last set power; DMCC can't read back power (yet!)
        if self.is_testing:
            self._position = 0  # last set position, only when testing
            self._velocity = 0  # last set velocity, only when testing

        self.logger.debug("Setup {}".format(self))

    @property
    def voltage(self):
        """Return the motor supply voltage connected to the board.

        :returns: Motor supply voltage (volts).

        """
        return self.dmcc.voltage()


    @property
    def power(self):
        """Return the current motor power.

        :returns: The most recently set motor power

        """
        return self._power

    @power.setter
    def power(self, value):
        """Set the power level of this motor.

        :param value: Desired motor power [-100,100]
        :type value: float

        """
        # NB: don't use logging that involves expensive formatting
        self.logger.debug("Setting motor %d-%d power to %d",
                self.dmcc.cape_num, self.motor_num, value)
        self.motor = value
        self._power = value  # if someone asks later on

    @property
    def position(self):
        """Return the current motor position (encoder ticks).

        :returns: Motor position in position_range (ticks).

        """
        if self.is_testing:
            return self._position
        return DMCC.getQEI(self.board_num, self.motor_num)
        # TODO: Ensure getQEI() actually returns ticks in position_range
        # TODO: Ensure setTargetPos() and getQEI() operate on the same units

    @position.setter
    def position(self, value):
        """Set the target position of this motor (encoder ticks).

        :param value: Desired motor position in position_range (ticks).
        :type value: int

        :returns: Boolean value indicating success.

        """
        value = self.position_range.clamp(value)
        if self.is_testing:
            self._position = value
            return True
        return DMCC.setTargetPos(
            self.board_num, self.motor_num, value) == 0

    @property
    def velocity(self):
        """Return the current motor velocity (encoder ticks per unit time).

        :returns: Motor velocity in velocity_range (ticks per sec).

        """
        if self.is_testing:
            return self._velocity
        return DMCC.getQEIVel(self.board_num, self.motor_num)
        # TODO: Ensure getQEIVel() actually returns ticks/sec in velocity_range
        # TODO: Ensure setTargetVel() and getQEIVel() operate on the same units

    @velocity.setter
    def velocity(self, value):
        """Set the target velocity of this motor (encoder ticks per sec).

        :param value: Desired motor velocity in velocity_range (ticks per sec).
        :type value: int

        :returns: Boolean value indicating success.

        """
        value = self.velocity_range.clamp(value)
        if self.is_testing:
            self._velocity = value
            return True
        return DMCC.setTargetVel(
            self.board_num, self.motor_num, value) == 0

    def setPID(self, target, P, I, D):
        """Set PID target parameter (position or velocity) and constants.
        NOTE: Call specialized methods setXXXPID() instead of this directly.

        :param target: Desired parameter to control (0=position, 1=velocity).
        :type target: int
        :param P: Proportional gain constant.
        :type int:
        :param I: Integral gain constant.
        :type int:
        :param D: Differential gain constant.
        :type int:

        :returns: Boolean value indicating success.

        """
        if self.is_testing:
            return True
        return DMCC.setPIDConstants(self.board_num, self.motor_num,
                                    target, P, I, D) == 0

    def setPositionPID(self, P, I, D):
        """Set PID constants to control position [see setPID()]."""
        return self.setPID(0, P, I, D)

    def setVelocityPID(self, P, I, D):
        """Set PID constants to control velocity [see setPID()]."""
        return self.setPID(1, P, I, D)

    def __str__(self):
        """Returns basic motor ID information as a string."""
        # NOTE: Properties (position, velocity) would be slow to read
        return "{}: {{ DMCC: {} motor_num: {} }}".format(
            self.__class__.__name__, self.dmcc.cape_num, self.motor_num)


