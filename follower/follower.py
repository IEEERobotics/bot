"""Logic for line following."""

import sys

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod
import lib.exceptions as ex


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
