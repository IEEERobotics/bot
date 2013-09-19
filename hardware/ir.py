"""Abstraction layer for line-following IR arrays."""

import lib.lib as lib

NUM_IRS = 16

class IR(object):

    """Class for abstracting IR sensors.

    The current plan is to use two 8 bit IR sensors on each side
    of the bot. This class will allow that pair of sensors to be
    addressed as a single unit.

    Currently a stub, waiting for working IR sensors to be built.

    """

    def __init__(self, ID):
        """Setup required pins and get logger.

        The current required pins are not known, so this is a stub.

        :param ID: Identifier for this IR array.
        :type ID: string

        """
        # Store ID of this IR array
        self.ID = ID

        # Get and store logger object
        self.logger = lib.get_logger()

        # Warn user that this code is only a stub
        self.logger.warn("IR abstraction not implemented, will return all 0s")

    def __str__(self):
        """Returns human-readable representation.

        :returns: String giving ID of IR array.

        """
        return "IR ID: {}".format(self.ID)

    def get_reading(self):
        """Poll IR sensors and return sensed information.

        Note that this is currently a stub.

        :returns: Readings from the 16 IR sensors managed by this object.

        """
        reading = {}
        for i in range(NUM_IRS):
            # TODO: Actually poll pins here, once IR arrays are built
            reading["ir_" + str(i)] = 0
        self.logger.debug("IR id={} reading: {}".format(self.ID, reading))
        return reading
