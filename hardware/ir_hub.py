"""Abstraction of all line-following arrays as one unit."""

import lib.lib as lib
import hardware.ir as ir_mod


class IRHub(object):
    """Class for abstracting all IR arrays and working with them as a unit.

    ir.IR is currently encapsulates one IR sensor array using a
    MUX select scheme.

    """

    def __init__(self):
        """Build IR array abstraction objects and logger."""
        # Get and store logger object
        self.logger = lib.get_logger()

        # Load system configuration
        config = lib.load_config()

        # Read mapping (dict) of IR array names to input ADC pins from config
        # NOTE: IR unit select lines are common
        ir_input_adcs = config["ir_input_adcs"]
        #array_names = ["front", "back", "left", "right"]

        # Create IR array objects
        self.arrays = {}
        for name, pin in ir_input_adcs.iteritems():
            self.arrays[name] = ir_mod.IRArray(name, pin)

    def __str__(self):
        """Returns human-readable representation of IRHub.

        :returns: Info about each IR array owned by this IRHub.

        """
        return "IRHub:- {}".format("; ".join(str(array)
                                   for array in self.arrays.itervalues()))

    def read_all_arrays(self):
        """Get readings from all IR arrays.

        :returns: Readings from all IR arrays managed by this object.

        """
        readings = {}
        for name, array in self.arrays.iteritems():
            # read_all_units() logs currently read values
            readings[name] = array.read_all_units()
        #self.logger.debug("IR readings: {}".format(readings))  # [debug]
        return readings
