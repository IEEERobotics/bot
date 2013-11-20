"""Abstraction of all line-following arrays as one unit."""

import time
import lib.lib as lib
import ir_analog as ir_analog_mod
import ir_digital as ir_digital_mod
import pybbb.bbb.gpio as gpio_mod

ord_zero = ord('0')  # Cached ordinal value of zero, for efficiency

class IRHub(object):

    """Class for abstracting all IR arrays and working with them as a unit.

    This abstraction owns four IR arrays, each a subclass of IRArray. They
    can be digital or analog arrays, as the difference between the two is
    hidden at this level of abstraction.

    The way that IR values are read is somewhat complex because of our
    highly optimized hardware configuration. The two sets of pins used
    to work with the IR arrays fall into to categories: GPIO select lines 
    and GPIO pins used to read values.

    To walk though an example, a number between 0 and num_ir_units-1 is
    written to the select lines, which changes the value being reported
    for every array. That's important to internalize - writing a single
    select value changes which IR sensor on each array is being reported
    by the read GPIO of that IR array. So, iterating over the range of
    select values, each array managed by this abstraction should be read
    at each step of the iteration. Once num_ir_units iterations over the
    select values have been completed, with each array read at each step,
    the read process has completed.

    """

    num_ir_units = 16 #  Number of IR sensors on an array

    def __init__(self):
        """Build IR array abstraction objects."""
        # Load config and logger
        self.logger = lib.get_logger()
        config = lib.load_config()

        # Number of IR sensors on an array
        self.num_ir_units = config["irs_per_array"]

        # Build GPIO pins used to select which IR units are active
        if config["testing"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir_base = config["test_gpio_base_dir"]

            # Build GPIOs used for selecting active IR units in test mode
            self.select_gpios = [gpio_mod.GPIO(gpio, gpio_test_dir_base)
                                    for gpio in config["ir_select_gpios"]]
        else:
            try:
                # Build GPIOs used for selecting active IR units
                self.select_gpios = [gpio_mod.GPIO(gpio)
                                        for gpio in config["ir_select_gpios"]]
            except Exception as e:
                self.logger.error("GPIOs could not be initialized. " +
                                  "Not on the bone? Run unit test instead. " +
                                  "Exception: {}".format(e))
 
        # Read mapping (dict) of IR array names to input GPIO pins from config
        # NOTE: IR unit select lines are common
        # TODO: Update to use GPIOs in config once GPIOs are known
        ir_analog_input_gpios = config["ir_analog_input_gpios"]
        ir_digital_input_gpios = config["ir_digital_input_gpios"]

        # Create IR array objects
        self.arrays = {}
        for name, gpio in ir_analog_input_gpios.iteritems():
            self.arrays[name] = ir_analog_mod.IRAnalog(name, gpio)

        for name, gpio in ir_digital_input_gpios.iteritems():
            self.arrays[name] = ir_digital_mod.IRDigital(name, gpio)

        # Create buffer to store readings from all sensor units
        self.reading = {}
        for array_name in self.arrays.keys():
            self.reading[array_name] = [0] * 16

    def __str__(self):
        """Returns human-readable representation of IRHub.

        :returns: Info about each IR array owned by this IRHub.

        """
        return "IRHub:- {}".format("; ".join(str(array)
                                   for array in self.arrays.itervalues()))

    def select_nth_units(self, n):
        """Selects IR sensor unit (0 to num_ir_units-1).

        Note that this applies to all arrays. So, selecting unit n
        implies selecting it for all arrays managed by this abstraction.

        """
        # Use binary string directly; more efficient
        # TODO: Use bitarray instead: https://pypi.python.org/pypi/bitarray/
        line_val = "{:04b}".format(n)

        for gpio, value in zip(self.select_gpios, line_val):
            gpio.value = ord(value) - ord_zero

    def read_nth_units(self, n):
        """Read the currently selected IR units on each array.

        Note that a single select line configuration allows the reading
        of the nth unit on every array, so the n units managed by each array
        only need to be looped over once, since this method reads every
        array's nth unit per call.

        The method updates the cached reading value for the nth unit
        of each array managed by this abstraction.

        """
        self.select_nth_units(n)

        for name, array in self.arrays.iteritems():
            # TODO: There's a logic error here. Need to append to list.
            self.reading[name] = array.selected_unit_val

    def read_all(self):
        """Poll IR sensor units and return sensed information.

        Note: Caller should make a copy if a read_all_units() is executed
        while previous values are being used.

        :returns: Readings from all IR sensor units managed by this object.

        """
        # TODO more efficient loop using permutations?
        for unit_n in xrange(self.num_ir_units):
            self.read_nth_units(unit_n)
        self.logger.debug("IR reading: {}".format(self.reading))
        return self.reading


def read_loop(delay=1):
    """Read IR array values using an IRHub object indefinitely.

    To be used interactively on bot for testing IR arrays, not in other code.

    :param delay: Time in seconds to wait between IR reads
    :type delay: float

    """
    hub = IRHub()
    print "Starting read loop... [Ctrl+C to quit]"
    while True:
        try:
            readings = hub.read_all()
            print "\nIR Readings:-"
            print "\n".join("{}: {}".format(name, reading)
                            for name, reading in readings.iteritems())
            time.sleep(delay)
        except KeyboardInterrupt:
            print "Quitting..."
            break
    print "Done."


if __name__ == "__main__":
    read_loop()
