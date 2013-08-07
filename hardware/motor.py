"""Abstraction layer for motors."""

import lib.lib as lib
import pybbb.bbb.pwm as pwm_mod

class Motor(object):
    """Class for abstracting motor settings."""

    def __init__(self, num):
        """Setup logger and PWM interface.

        :param num: ID number of this motor. Also defines PWM number.
        :type num: int

        """
        # Get and store logger object
        self.logger = lib.get_logger()
        self.logger.debug("Motor {} has logger".format(num))

        self.num = num

        self.pwm = pwm_mod.pwm(num)
        self.logger.debug("Built {}".format(str(self.pwm)))

        self._speed = self.pwm.duty
        self.logger.debug("Motor {} speed: {}".format(num, self._speed))
        self._direction = self.pwm.polarity
        self.logger.debug("Motor {} direction: {}".format(num, self._direction))

    @property
    def speed(self):
        """Getter for motor's speed as % of max (same as duty cycle)."""
        return self.pwm.duty

    @speed.setter
    def speed(self, speed):
        """Setter for motor's speed as % of max (same as duty cycle).

        :param speed: Speed to set motor to in % of maximum.
        :type speed: int

        """
        self.pwm.duty = speed
        self.logger.debug("Set motor {} speed to {}".format(self.num, speed))

    @property
    def direction(self):
        """Getter for motor's direction (same as polarity)."""
        return self.pwm.polarity

    @direction.setter
    def direction(self, direction):
        """Setter for motor's direction (same as polarity).

        :param direction: Direction to rotate motors (1=forward, 0=reverse).
        :type direction: int

        """
        self.pwm.polarity = direction
        self.logger.debug("Set motor {} direction to {}".format(self.num, direction))

