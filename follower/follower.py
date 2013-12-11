"""Logic for line following."""

import sys

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod


class Follower(object):

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build Ir arrays, logger and drivers."""
        self.logger = lib.get_logger()
        self.driver = mec_driver_mod.MecDriver()
        self.ir_hub = ir_hub_mod.IRHub()

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
            if reading_contains_pattern([1,1],array):
                return {"line_found":True, "time_elapsed": time() - start_time}
            if time() - start_time > max_time:
                return {"found_line": False, "time_elapsed": time() - start_time}
