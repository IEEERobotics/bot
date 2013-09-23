"""Abstraction layer for line-following IR arrays."""

import lib.lib as lib
import pybbb.bbb.gpio as gpio_mod
import pybbb.bbb.adc as adc_mod

num_ir_units = 16  # Number of IR sensor units in one array
ord_zero = ord('0')  # Cached ordinal value of zero, for efficiency


class IRArray(object):
    """Class for abstracting IR sensors.

    The current plan is to use two 8 bit IR sensors on each side
    of the bot. This class will allow that pair of sensors to be
    addressed as a single unit.

    Currently a stub, waiting for working IR sensors to be built.

    """

    def __init__(self, name):
        """Setup required pins and get logger.

        The current required pins are not known, so this is a stub.

        :param name: Identifier for this IR array.
        :type name: string

        """
        # Store name of this IR array
        self.name = name

        # Get and store logger object
        self.logger = lib.get_logger()

        # Load system configuration
        config = lib.load_config()

        # Create GPIO and ADC objects
        if config["testing"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir_base = lib.prepend_prefix(
                                            config["test_gpio_base_dir"])
            adc_test_dir = lib.prepend_prefix(config["test_adc_base_dir"])

            # Build GPIO and ADC objects for testing
            self.ir_select_gpios = [gpio_mod.GPIO(gpio, gpio_test_dir_base)
                                    for gpio in config["ir_select_gpios"]]
            self.ir_input_adc = adc_mod.ADC(config["ir_input_adc"],
                                            adc_test_dir + '/AIN')
        else:
            try:
                self.ir_select_gpios = [gpio_mod.GPIO(gpio)
                                        for gpio in config["ir_select_gpios"]]
                self.ir_input_adc = adc_mod.ADC(config["ir_input_adc"])
            except Exception as e:
                self.logger.error("GPIOs & ADC could not be initialized. " +
                                  "Not on the bone? Run unit test instead. " +
                                  "Exception: {}".format(e))

        # Create buffer to store readings from all sensor units
        self.reading = [0] * num_ir_units

    def __str__(self):
        """Returns human-readable representation.

        :returns: String giving name of IR array.

        """
        return "{}: {}".format(self.name, self.reading)

    def select_lines(self, values):
        """Set select lines (GPIO pins) to given values.

        :param values: Binary iterable with length at least that
            of ir_select_gpios (ideally the same).
        :type ID: iterable

        """
        for gpio, value in zip(self.ir_select_gpios, values):
            gpio.value = value

    def select_lines_str(self, values_str):
        """Efficient version of select_lines, directly uses a binary string."""
        for gpio, value in zip(self.ir_select_gpios, values_str):
            gpio.value = ord(value) - ord_zero

    def select_unit(self, unit):
        """Selects IR sensor unit (0-15)."""
        # Convert unit number to array of 0s and 1s
        #self.select_lines([int(x) for x in "{:04b}".format(unit)])
        # Use binary string directly; more efficient
        self.select_lines_str("{:04b}".format(unit))
        # TODO: Use bitarray instead: https://pypi.python.org/pypi/bitarray/

    def read_adc(self):
        """Read the currently selected IR unit on the input ADC line."""
        return self.ir_input_adc.read()

    def read_unit(self, unit):
        """Read a desired IR sensor unit."""
        # TODO: Do we need a short sleep to let ADC measure value correctly?
        self.select_unit(unit)
        return self.read_adc()

    def read_all_units(self):
        """Poll IR sensor units and return sensed information.

        :returns: Readings from all IR sensor units managed by this object.

        """
        # TODO: Zero out self.reading?
        # TODO more efficient loop using permutations?
        for unit in xrange(num_ir_units):
            self.reading[unit] = self.read_unit(unit)
        self.logger.debug("IR reading:- ".format(self))
        # NOTE: Caller should make a copy if a read_all() is executed
        # while previous values are being used
        return self.reading
