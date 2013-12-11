"""Logic for line following."""

import sys
import lib.lib as lib
from time import time
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod


class Follower(object):

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build Ir arrays, logger and drivers."""
        self.logger = lib.get_logger()
        self.ir_hub = ir_hub_mod.IRHub()
        self.driver = mec_driver_mod.MecDriver()

    def follow(self, state_table):
        """Accept and handle fire commands.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        :param state_table: Data describing current heading.
        
        """
        self.logger.error("The follow method must be overridden by a subclass")
        raise NotImplementedError("Subclass must override this method")

    def reading_contains_pattern(self, pattern, reading):
        """Search the given reading for the given pattern.

        :param pattern: Pattern to search reading for. For example, [1, 1] for a pair of consecutive ones.
        :type pattern: list
        :param reading: IR array reading to search for the given pattern. Should contain only 0s and 1s.
        :type reading: list
        :returns: True if the pattern is in the reading, False otherwise.

        """
        return "".join(map(str, pattern)) in "".join(map(str, reading))

    def watch_for_line(self, max_time):
        """Recieves time period for which to continuously watch for line.
        Returns True when line is found.
        Returns False if line is not found before time is hit.
        """
        start_time = time()
        while True:
            reading = self.ir_hub.read_all()
            for name, array in reading.iteritems():
                if self.reading_contains_pattern([1,1],array):
                    return {"line_found":True, "time_elapsed": time() - start_time}
                if time() - start_time > max_time:
                    return {"line_found": False, "time_elapsed": time() - start_time}

    def oscillate(self, heading, osc_time=1):
        """Oscillate sideways, increasing in amplitude until line is found"""

        # Time in seconds for which bot oscillates in each direction.
        # Speed at which the bot is oscillating.
        # Increase in speed after each oscillation cycle.
        # Todo(Ahmed): Find reasonable constants.
        osc_speed = 10
        osc_increment = 10

        # The oscillation directions, perpendicular to parameter "heading"
        angle1 = heading + 90
        angle2 = heading - 90
        self.logger.debug("Pre-correction angles: angle1: {}, angle2: {}".format(
                                                                angle1, angle2))

        # Correct angles to fit bounds.
        angle1 %= self.driver.max_angle
        angle2 %= self.driver.max_angle
        self.logger.debug("Post-correction angles: angle1: {}, angle2: {}".format(
                                                                angle1, angle2))

        
        # Test headings for valid 0,360 values.
        assert 0 <= angle1 <= 360, "angle1 is {}".format(angle1)
        assert 0 <= angle2 <= 360, "angle2 is {}".format(angle2)

        # Todo: Consider making this a function call.
        line_not_found = True
        while line_not_found:

            # Drives in each direction.
            self.driver.move(osc_speed, angle1)
            # Passes control to find line, which moves until it finds line or runs out of time.
            # Note: watch_for_line returns "line_found" (bool) and "time_elapsed" (int)
            results = self.watch_for_line(osc_time)
            self.driver.move(0,0)

            if results["line_found"]:
                line_not_found = False

            # Search in other direction.
            self.driver.move(osc_speed, angle2)
            # "time elapsed" is used as max_time for more precise movements.
            results = self.watch_for_line(results["time_elapsed"]*2)
            self.logger.debug("Oscillation direction 1: osc_speed: {}, heading: {}".format(osc_speed,
                                                                                        heading))
            self.driver.move(0,0)         
            if results["line_found"]:
                line_not_found = False


            # If line is not found, Continue looping until line is found.
            # For now, stop when max speed is hit.
            osc_speed += 90
            if osc_speed >= self.driver.max_speed:
                line_not_found = False
