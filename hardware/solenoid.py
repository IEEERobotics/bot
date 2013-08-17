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
        :param testing: If True, use test HW dir given by config, else real HW.
        :type testing: boolean

        """
        # Get and store logger object
        self.logger = lib.get_logger()

        # Store ID number of solenoid
        self.num = num

        # Load system configuration
        config = lib.load_config()

        if config["testing"]:
            self.logger.debug("TEST MODE: Solenoid {}".format(self.num))

            # Get dir of simulated hardware files from config
            test_dir = lib.prepend_prefix(config["test_gpio_base_dir"])
            self.logger.debug("Test GPIO base dir: {}".format(test_dir))

            # Build GPIO object for BBB interaction, provide test dir
            self.gpio = gpio_mod.GPIO(self.num, test_dir)
            self.logger.debug("Built {}".format(self.gpio))
        else:
            self.logger.debug("EMBEDDED MODE: Solenoid {}".format(self.num))

            # Build GPIO object for BBB interaction
            self.gpio = gpio_mod.GPIO(self.num)
            self.logger.debug("Built {}".format(self.gpio))

        # Set GPIO to output signal
        self.gpio.output()

        # Set solenoid to be initially retracted
        self.retract()
        self.logger.debug("Setup {}".format(self))

    def __str__(self):
        """Override string representation of this object for readability.

        :returns: Human readable representation of this object.

        """
        return "Solenoid #{}: {}".format(self.num, self.state)

    def extend(self):
        """Set solenoid to extended position."""
        self.gpio.value = EXTENDED

    def retract(self):
        """Set solenoid to retracted position."""
        self.gpio.value = RETRACTED

    @property
    def state(self):
        """Getter for state of the solenoid (extended/retracted).

        :returns: State of the solenoid ("extended" or "retracted").

        """
        val = self.gpio.value
        if val == RETRACTED:
            return "retracted"
        elif val == EXTENDED:
            return "extended"
        else:
            self.logger.error("Invalid GPIO state: {}".format(val))
