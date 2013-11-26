"""Abstraction of all ultrasonic sensors as one unit."""

import lib.lib as lib
import hardware.us as us_mod


class USHub(object):

    """Class for abstracting all ultrasonics, working with them as a unit."""

    def __init__(self):
        """Build ultrasonic abstraction objects and logger."""
        # Get and store logger object
        self.logger = lib.get_logger()

        # Load system configuration
        config = lib.get_config()

        # Create IR array objects
        self.USs = {}
        for name, params in config["ultrasonics"].iteritems():
            self.USs[name] = us_mod.US(name, params)

    def __str__(self):
        """Returns human-readable representation of USHub.

        :returns: Info about each ultrasonic sensor owned by this USHub.

        """
        return "USHub: {}".format("; ".join(str(us)
                                   for us in self.USs.itervalues()))

    def read_all(self):
        """Get readings from all ultrasonic sensors.

        :returns: Readings from all ultrasonic sensors managed by this object.

        """
        readings = {}
        for position, us in self.USs.iteritems():
            readings[position] = us.distance
        self.logger.debug("USHub readings: {}".format(readings))
        return readings
