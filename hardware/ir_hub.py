"""Abstraction of all line-following arrays as one unit."""

from time import time, sleep

import pybbb.bbb.gpio as gpio_mod

import lib.lib as lib
import ir_analog as ir_analog_mod


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

    num_ir_units = 16  # Number of IR sensors on an array

    def __init__(self):
        """Build IR array abstraction objects."""
        # Load config and logger
        self.logger = lib.get_logger()
        config = lib.get_config()

        # Number of IR sensors on an array
        self.num_ir_units = config["irs_per_array"]

        # Swap halves of each 16-unit array or not
        # TODO: Remove this once corrected in hardware (see: select_nth_units)
        self.ir_swap_halves = config["ir_swap_halves"]

        # Pause between each select-read operation to let ADCs settle
        self.ir_read_delay = config["ir_read_delay"]

        # Use accurate reading (ADC) or not (GPIO)
        self.ir_read_adc = config["ir_read_adc"]

        # Verbose output flag
        self.ir_verbose_output = config["ir_verbose_output"]
        if self.ir_verbose_output:
            self.logger.info("Verbose output enabled")

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
        ir_analog_input_gpios = config["ir_analog_input_gpios"]

        # Create IR array objects
        self.arrays = {}
        for name, gpio in ir_analog_input_gpios.iteritems():
            try:
                self.arrays[name] = ir_analog_mod.IRAnalog(name, gpio)
            except IOError:
                self.logger.error("Unable to create {} IR array".format(name))
                self.arrays[name] = None

        # Create buffer to store readings from all sensor units
        self.reading = {}
        for array_name in self.arrays.keys():
            self.reading[array_name] = [0] * 16

        self.last_read_time = None

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

        :param n: IR unit to select, between 0 and num_ir_units-1.
        :type n: int
        :raises ValueError: If n isn't between 0 and num_ir_units-1

        """
        if n < 0 or n >= self.num_ir_units:
            self.logger.error("Invalid value of n: {}".format(n))
            raise ValueError("n must be between 0 and num_ir_units-1")

        # Flip MSB to effectively swap array halves, if necessary
        if self.ir_swap_halves:
            n ^= 8  # assumes 4 select lines, so MSB = 1000 = 8

        # Use binary string directly; more efficient
        line_val = "{:04b}".format(n)

        for gpio, value in zip(self.select_gpios, line_val):
            gpio.value = int(value)

    def read_nth_units(self, n):
        """Read the currently selected IR units on each array.

        Note that a single select line configuration allows the reading
        of the nth unit on every array, so the n units managed by each array
        only need to be looped over once, since this method reads every
        array's nth unit per call.

        The method updates the cached reading value for the nth unit
        of each array managed by this abstraction.

        :param n: IR unit to read, between 0 and num_ir_units-1.
        :type n: int
        :raises ValueError: If n isn't between 0 and num_ir_units-1

        """
        if n < 0 or n >= self.num_ir_units:
            self.logger.error("Invalid value of n: {}".format(n))
            raise ValueError("n must be between 0 and num_ir_units-1")

        self.select_nth_units(n)
        sleep(self.ir_read_delay)  # let ADCs settle

        for name, array in self.arrays.iteritems():
            if array is None:
                continue

            if self.ir_verbose_output:
                # Read both ADC & GPIO and display values
                adc_result = array.read_adc_result()  # NOTE IRAnalog array
                gpio_result = array.selected_unit_val
                self.reading[name][n] = adc_result \
                                            if self.ir_read_adc \
                                            else array.selected_unit_val
                self.logger.info("IR ({}, {}) ADC: {}, GPIO: {}".format(
                                            name, n, adc_result, gpio_result))
            else:
                # Read only one, ADC or GPIO
                self.reading[name][n] = array.read_adc_result() \
                                            if self.ir_read_adc \
                                            else array.selected_unit_val

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
        self.last_read_time = time()
        return self.reading

    def read_cached(self, max_staleness=1):
        """Get cached IR data if it's fresher than param, else read IRs.

        :param max_staleness: Return cache if it's fresher than this (secs).
        :type max_staleness: float
        :returns: Dict with IR data, read time and flag if read was required.

        """
        if self.last_read_time is None:
            # Handles when read_all hasn't been called
            self.read_all()
            fresh = True
        elif time() - self.last_read_time <= max_staleness:
            fresh = False
        else:
            self.read_all()
            fresh = True
        return {"readings": self.reading, "time": self.last_read_time,
            "fresh": fresh}


def live_read_loop(delay=0.25, accurate=False):
    # Reconfiguration (NOTE: Need to do this before instantiating IRHub)
    config = lib.get_config()
    config["ir_verbose_output"] = True
    if accurate:
        print "ir_hub.live_read_loop(): Requesting accurate IR values (ADC)"
        config["ir_read_adc"] = True
    
    # Instantiate IRHub object and run infinite read loop
    hub = IRHub()
    print "ir_hub.live_read_loop(): Starting read loop... [Ctrl+C to exit]"
    while True:
        try:
            readings = hub.read_all()
            print "\n{}".format(time())
            print "\n".join("{}: {}".format(name, reading)
                            for name, reading in readings.iteritems())
            sleep(delay)
        except KeyboardInterrupt:
            print "ir_hub.live_read_loop(): Interrupted; exiting..."
            break


if __name__ == "__main__":
    print "ir_hub.__main__: Running live read loop"
    live_read_loop(accurate=True)
