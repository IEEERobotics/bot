"""Abstraction layer for ultrasonic sensors"""

import lib.lib as lib


class US(object):

    """Class for abstracting ultrasonic sensors.

    Currently a stub, need info about how US sensors connect to bot.

    """

    def __init__(self, ID):
        """Setup required pins and get logger.

        The required pins are not known, so this is a stub.

        :param ID: Identifier for this ultrasonic sensor.
        :type ID: string

        """
        # Store ID of this ultrasonic sensor
        self.ID = ID

        # Get and store logger object
        self.logger = lib.get_logger()

        # Warn user that this code is only a stub
        self.logger.warn("US abstraction not implemented, range will be 0.")

    def __str__(self):
        """Represent ultrasonic sensor in human-readable format.

        :returns: String giving ID and range of ultrasonic sensor.

        """
        return "Ultrasonic ID: {}, range: {}".format(self.ID, self.distance)

    @property
    def distance(self):
        """Getter for ultrasonic sensor range.

        This is a stub and will always return 0. Details of connecting
        to US sensor are needed before this can be fully implemented.

        :returns: Range reported by ultrasonic sensor in CM.

        """
        return 0
