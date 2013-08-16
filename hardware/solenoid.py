"""Abstraction layer for solenoids."""

import pybbb.bbb.gpio as gpio_mod

import lib.lib as lib

EXTENDED = 0
RETRACTED = 1


class Solenoid(object):
    """Class for abstracting solenoid settings."""

    def __init__(self, num, testing=False):
        """Setup logger and GPIO interface.

        :param num: ID number of this solenoid. Also defines GPIO number.
        :type num: int
        :param testing: If True, use test hw dir given by config, else real hw.
        :type testing: boolean

        """
        # Get and store logger object
        self.logger = lib.get_logger()
        self.logger.debug("Solenoid {} has logger".format(num))

        # Store ID number of solenoid
        self.num = num

        if testing:
            self.logger.debug("TEST MODE: Solenoid {}".format(num))

            # Load system configuration
            config = lib.load_config()

            # Get dir of simulated hardware files from config
            test_dir = lib.prepend_prefix(config["test_gpio_base_dir"])
            self.logger.debug("Test GPIO base dir: {}".format(test_dir))

            # Build GPIO object for BBB interaction, provide test dir
            self.gpio = gpio_mod.GPIO(num, test_dir)
            self.logger.debug("Built {}".format(str(self.gpio)))
        else:
            self.logger.debug("EMBEDDED MODE: Solenoid {}".format(num))

            # Build GPIO object for BBB interaction
            self.gpio = gpio_mod.GPIO(num)
            self.logger.debug("Built {}".format(str(self.gpio)))

        # Set GPIO to output signal
        self.gpio.output()
        self.logger.debug("{} set to output".format(str(self.gpio)))

    def __str__(self):
        return "Solenoid #{}: {}".format(self.num, self.state)

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
            return "retracted"
        elif val == EXTENDED:
            return "extended"
        else:
            self.logger.error("Invalid GPIO state: {}".format(val))
