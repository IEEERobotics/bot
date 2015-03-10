"""Abstraction layer for solenoids."""

import bbb.gpio as gpio_mod

import bot.lib.lib as lib

EXTENDED = 0
RETRACTED = 1


class Solenoid(object):

    """Class for abstracting solenoid settings."""

    def __init__(self, gpio_num):
        """Setup logger and GPIO interface.

        :param gpio_num: GPIO number used by this solenoid.
        :type gpio_num: int

        """
        # Get and store logger object
        self.logger = lib.get_logger()

        # Store ID number of solenoid
        self.gpio_num = gpio_num

        # Load system configuration
        config = lib.get_config()

        if config["test_mode"]["solenoid"]:
            # Get dir of simulated hardware files from config
            test_dir = config["test_gpio_base_dir"]

            # Build GPIO object for BBB interaction, provide test dir
            self.gpio = gpio_mod.GPIO(self.gpio_num, test_dir)
        else:
            # Build GPIO object for BBB interaction
            self.gpio = gpio_mod.GPIO(self.gpio_num)

        # Set GPIO to output signal
        self.gpio.output()

        # Set solenoid to be initially retracted
        self.retract()
        self.logger.debug("Setup {}".format(self))

    def __str__(self):
        """Override string representation of this object for readability.

        :returns: Human readable representation of this object.

        """
        return "Solenoid #{}: {}".format(self.gpio_num, self.state)

    def extend(self):
        """Set solenoid to extended position."""
        self.logger.debug("Extending {}".format(self))
        self.gpio.value = EXTENDED

    def retract(self):
        """Set solenoid to retracted position."""
        self.logger.debug("Retracting {}".format(self))
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
