"""Abstraction of all line-following arrays as one unit."""

import lib.lib as lib
import hardware.ir as ir_mod

class IRHub(object):

    """Class for abstracting all IR arrays and working with them as a unit.

    ir.IR is currently a stub, waiting for working IR sensors to be built.

    """

    def __init__(self):
        """Build IR abstraction objects and logger."""
        # Get and store logger object
        self.logger = lib.get_logger()

        array_names = ["front", "back", "left", "right"]
        self.arrays = {}
        for name in array_names:
            self.arrays[name] = ir_mod.IR()

    def get_reading(self):
        """Get readings from all IR arrays.

        Note that this is currently a stub.

        :returns: Readings from the 16 IR sensors managed by this object.

        """
        reading = {}
        for name, array in self.arrays.iteritems():
            reading[name] = array.get_reading()
        self.logger.debug("IR arrays: {}".format(reading))
        return reading
