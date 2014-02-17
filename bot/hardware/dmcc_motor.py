")""Abstraction layer for DMCC-based motors."""

from collections import defaultdict

import pyDMCC

import bot.lib.lib as lib


class DMCCMotorSet(dict):
    """A single interface to a collection of DMCCs and associated motors."""

    def __init__(self, motor_config):
        """Initialize a set of DMCCs and their associated motors

        :param motor_config: Config entry mapping motor names to DMCC ids and
        motor indices

        Dictionary entries are in the format:
            <motor_name>: { board_num: [0-3], motor_num: [1-2] }

        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()
        self.is_testing = self.config["test_mode"]["DMCC"]

        # print "Testing: ", self.config["testing"]
        # print pyDMCC.lib._config

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
            dmccs = defaultdict(
                lambda: pyDMCC.DMCC(
                    0, verify=False, bus=None, logger=self.logger))

        self.motors = {}
        for name, conf in motor_config.items():
            if 'invert' in conf.keys():
                invert = conf['invert']
            else:
                invert = False
            try:
                self.motors[name] = DMCCMotor(
                    dmccs[conf['board_num']], conf['motor_num'], invert)
            except KeyError:
                self.logger.error(
                    "Bad motor definition for motor: '{}'".format(
                        name))
                raise KeyError

        self.logger.debug("Setup {}".format(self))

    def __getitem__(self, index):
        return self.motors[index]

    def __str__(self):
        return "{} for motors: {}".format(self.__class__.__name__,
                                          self.motors.keys())


class DMCCMotor(object):

    def __init__(self, dmcc, motor_num, invert=False):
        """Wraps an individual pyDMCC motor

        :param dmcc: Controlling pyDMCC.DMCC object, None when testing
        :param motor_num: Motor number in motor_num_range.
        :param invert: Set to True if all values should be inverted
        :type motor_num: int

        Attribute real_motor is the instantiated pyDMCC.Motor

        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.is_testing = self.config["testing"]

        self.dmcc = dmcc
        self.real_motor = dmcc.motors[motor_num]
        self.motor_num = motor_num
        self.invert = invert
        if invert:
            self.inversion_multiplier = -1
        else:
            self.inversion_multiplier = 1

        if self.is_testing:
            self._pos_kP = self._pos_kI = self._pos_kD = 0
            self._vel_kP = self._vel_kI = self._vel_kD = 0
        else:
            self._pos_kP, self._pos_kI, self._pos_kD \
                = self.real_motor.position_pid
            self._vel_kP, self._vel_kI, self._vel_kD \
                = self.real_motor.velocity_pid

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

        The DMCC boards don't support querying power directly (the I2C
        register is alway zero), so we have to keep track of this ourselves.

        """
        return self._power * self.inversion_multiplier

    @power.setter
    def power(self, value):
        """Set the power level of this motor.

        :param value: Desired motor power [-100,100]
        :type value: float

        """
        # NB: don't use logging that involves expensive formatting
        value *= self.inversion_multiplier
        self.logger.debug(
            "Setting motor %d-%d power to %d",
            self.dmcc.cape_num, self.motor_num, value)

        # We can't query the power setting, even from a physcial DMCC,
        # so we always have to do our own bookkeeping
        self._power = value
        if not self.is_testing:
            self.real_motor.power = value

    @property
    def position(self):
        """Return the current motor position (encoder ticks).

        :returns: Motor position in position_range (ticks).

        """
        if self.is_testing:
            val = self._position
        else:
            val = self.real_motor.position
        return val * self.inversion_multiplier

    @position.setter
    def position(self, value):
        """Set the target position of this motor (encoder ticks).

        :param value: Desired motor position in position_range (ticks).
        :type value: int

        :returns: Boolean value indicating success.

        """
        value *= self.inversion_multiplier
        if self.is_testing:
            self._position = value
        self.real_motor.position = value

    @property
    def velocity(self):
        """Return the current motor velocity (encoder ticks per unit time).

        :returns: Motor velocity in velocity_range (ticks per sec).

        """
        if self.is_testing:
            val = self._velocity
        else:
            val = self.real_motor.velocity
        return val * self.inversion_multiplier

    @velocity.setter
    def velocity(self, value):
        """Set the target velocity of this motor (encoder ticks per sec).

        :param value: Desired motor velocity in velocity_range (ticks per sec).
        :type value: int

        :returns: Boolean value indicating success.

        """

        value *= self.inversion_multiplier
        self.logger.debug(
            "Setting motor %d-%d velociy to %d",
            self.dmcc.cape_num, self.motor_num, value)
        # Verify that we've set meaningful PID constants
        if self._vel_kP == 0:
            self.logger.warning(
                "Can't set motor %d-%d velocity: kP not set.",
                self.dmcc.cape_num, self.motor_num)
            raise RuntimeError

        if self.is_testing:
            self._velocity = value
        else:
            self.real_motor.velocity = value

    def setPositionPID(self, P, I, D):
        """Set PID constants to control position."""
        self._pos_kP = P
        self._pos_kI = I
        self._pos_kD = D
        if not self.is_testing:
            self.real_motor.position_pid = (P, I, D)

    def setVelocityPID(self, P, I, D):
        """Set PID constants to control velocity."""
        self._vel_kP = P
        self._vel_kI = I
        self._vel_kD = D
        if not self.is_testing:
            self.real_motor.velocity_pid = (P, I, D)

    def __str__(self):
        """Returns basic motor ID information as a string."""
        return "{}: {{ DMCC: {} motor_num: {} }}".format(
            self.__class__.__name__, self.dmcc.cape_num, self.motor_num)
