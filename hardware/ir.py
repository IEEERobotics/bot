"""Superclass for IR array abstractions."""

import lib.lib as lib
import pybbb.bbb.gpio as gpio_mod


class IRArray(object):
    """Superclass for IR array sensor abstractions.

    There are two 8-unit IR arrays on each of the four sides of the bot,
    which are abstracted in hardware into a 16 unit array. There are
    currently two types of arrays, one digital and one analog. This class
    acts as a superclass for the two types, as they are very similar and
    will be handled by IRHub as if they are identical.

    """

    def __init__(self, name, read_gpio_pin):
        """Setup required pins and get logger/config.

        Note that the value read on the read_gpio_pin will depend on
        the currently value on the GPIO select lines. IRHub manages
        the iteration over the select lines and the reading of each
        array's read_gpio at each step of the iteration.

        :param name: Identifier for this IR array.
        :type name: string
        :param read_gpio_pin: Pin used by array to read an IR unit.
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
            self.read_gpio = gpio_mod.GPIO(read_gpio_pin, gpio_test_dir)
        else:
            try:
                self.read_gpio = gpio_mod.GPIO(read_gpio_pin)
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
        All arrays should then be read to get each of their values for that
        line.

        To state it another way, an agent should iterate through the 16 select
        lines, calling this method on each of the four IR arrays at every
        iteration.

        :returns: 1/0, depending on the light under this array's selected IR.

        """
        return self.read_gpio.value
