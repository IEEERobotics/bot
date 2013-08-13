"""Abstraction layer for solenoids."""

import pybbb.bbb.gpio as gpio_mod

import lib.lib as lib

EXTENDED = 0
RETRACTED = 1


class Solenoid(object):
    """Class for abstracting solenoid settings."""

    def __init__(self, num):
        """Setup logger and GPIO interface.

        :param num: ID number of this solenoid. Also defines GPIO number.
        :type num: int

        """
        # Get and store logger object
        self.logger = lib.get_logger()
        self.logger.debug("Solenoid {} has logger".format(num))

        # Store ID number of solenoid
        self.num = num

        # Init state value to track GPIO/solenoid state
        self._state = None

        # Build GPIO object for BBB interaction
        self.gpio = gpio_mod.GPIO(num)
        self.logger.debug("Built {}".format(str(self.gpio)))

        # Set GPIO to output signal
        self.gpio.output()
        self.logger.debug("{} set to output".format(str(self.gpio)))

    def extend(self):
        """Set solenoid to extended position."""
        self.gpio.value = EXTENDED

    def retract(self):
        """Set solenoid to retracted position."""
        self.gpio.value = RETRACTED

    @property
    def state(self):
        """Getter for state of the solenoid (extended/retracted)."""
        val = self.gpio.value
        if val == RETRACTED:
            return = "retracted"
        elif val == EXTENDED:
            return = "extended"
        else:
            self.logger.error("Invalid GPIO state: {}".format(val))
