"""Module for handling high-level movement commands."""

import lib.lib as lib


class Driver(object):

    """Handle high-level movement commands."""

    def __init__(self):
        """Setup and store logger and config."""
        self.logger = lib.get_logger()
        self.config = lib.get_config()

    def move(self, desc):
        """Accept and handle a movement command.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        :param desc: Description of movement command to handle.
        :type desc: string

        """
        self.logger.error("The move method must be overridden by a subclass.")
        raise NotImplementedError("Subclass must override this method.")

    def jerk(self, desc):
        """Execute a rote forward movement.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        :param desc: Description of jerk command to handle.
        :type desc: string

        """
        self.logger.error("The jerk method must be overridden by a subclass.")
        raise NotImplementedError("Subclass must override this method.")
