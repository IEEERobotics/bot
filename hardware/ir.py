"""Superclass for IR array abstractions."""

import lib.lib as lib
import pybbb.bbb.gpio as gpio_mod


class IRArray(object):
    """Class for abstracting IR sensors.

    The current plan is to use two 8 bit IR sensors on each side
    of the bot. This class will allow that pair of sensors to be
    addressed as a single unit.

    Currently a stub, waiting for working IR sensors to be built.

    """

    def __init__(self, name, input_gpio_pin):
        """Setup required pins and get logger/config.

        :param name: Identifier for this IR array.
        :type name: string
        :param input_adc_pin: Input ADC pin number for this IR array.
        :type input_adc_pin: int

        """
        # Store name and input GPIO pin for this IR array
        self.name = name

        # Get logger and config
        self.logger = lib.get_logger()
        config = lib.load_config()

        # Create GPIO for reading sensed IR values
        if config["testing"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir = config["test_gpio_base_dir"]

            # Build GPIO object in test mode
            # TODO: Update config to reflect use of GPIOs
            self.input_gpio = gpio_mod.GPIO(input_gpio_pin, gpio_test_dir)
        else:
            try:
                self.input_gpio = gpio_mod.GPIO(input_gpio_pin)
            except Exception as e:
                self.logger.error("GPIOs could not be initialized. " +
                                  "Not on the bone? Run unit test instead. " +
                                  "Exception: {}".format(e))

    def __str__(self):
        """Returns human-readable representation.

        :returns: String giving info about IR array.

        """
        return "{} ({}): {}".format(
            self.name, self.input_gpio, self.selected_unit_val)

    @property
    def selected_unit_val(self):
        """Getter for the value of the currently selected IR unit.

        Note that it's the responsibility of IRHub to select the active line.
        All arrays should then be read to get each of their values for that line.

        To state it another way, an agent should iterate through the 16 select
        lines, calling this method on each of the four IR arrays at every
        iteration.

        :returns: 1/0, depending on the light under this array's selected IR.

        """
        return self.input_gpio.value
