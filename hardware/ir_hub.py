"""Abstraction of all line-following arrays as one unit."""

import lib.lib as lib
import hardware.ir as ir_mod


class IRHub(object):
    """Class for abstracting all IR arrays and working with them as a unit.

    ir.IR is currently encapsulates one IR sensor array using a MUX select scheme.

    """

    def __init__(self):
        """Build IR array abstraction objects and logger."""
        # Get and store logger object
        self.logger = lib.get_logger()

        # TODO: Array names and pins should be correlated and read from config
        array_names = ["front", "back", "left", "right"]
        self.arrays = {}
        for name in array_names:
            self.arrays[name] = ir_mod.IRArray(name)
            # TODO: A second parameter (5th select line?) is needed to select a particular IR array

    def __str__(self):
        """Returns human-readable representation of IRHub.

        :returns: Info about each IR array owned by this IRHub.

        """
        return "IRHub:- {}".format("; ".join(str(array) for array in self.arrays.itervalues()))

    def read_all_arrays(self):
        """Get readings from all IR arrays.

        :returns: Readings from all IR arrays managed by this object.

        """
        readings = {}
        for name, array in self.arrays.iteritems():
            readings[name] = array.read_all_units()  # read_all_units() logs currently read values
        #self.logger.debug("IR readings: {}".format(readings))  # no need to log again
        return readings
