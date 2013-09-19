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

        # TODO: Array names and pins should be correlated and read from config
        array_names = ["front", "back", "left", "right"]
        self.arrays = {}
        for name in array_names:
            self.arrays[name] = ir_mod.IR(name)

    def __str__(self):
        """Returns human-readable representation of IRHub.

        The convoluted way this is implemented seems necessary, as
        str(self.arrays) wouldn't propagate down to ir.IR.__str__.

        :returns: Info about each IR array owned by IRHub.

        """
        rep = "IRHub: "
        for name, array in self.arrays.iteritems():
            rep += "\"{}\" : \"{}\"; ".format(name, str(array))
        return rep[:len(rep) - 2]

    def get_reading(self):
        """Get readings from all IR arrays.

        Note that this is currently a stub.

        :returns: Readings from IR arrays managed by this object.

        """
        reading = {}
        for name, array in self.arrays.iteritems():
            reading[name] = array.get_reading()
        self.logger.debug("IR arrays: {}".format(reading))
        return reading
