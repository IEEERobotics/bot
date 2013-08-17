#!/usr/bin/env python
"""Module for handling high-level movement commands."""

import lib.lib as lib


class Driver(object):

    """Handle high-level movement commands."""

    def __init__(self):
        """Setup and store logger and config."""

        self.logger = lib.get_logger()
        self.logger.debug("Driver has logger")

        self.config = lib.load_config()
        self.logger.debug("Driver has config")

    def move(self, desc):
        """Accept and handle a movement command.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        :param desc: Description of movement command to handle.
        :type desc: string

        """
        self.logger.error("The move method must be overridden by a subclass.")
        raise NotImplementedError("Subclass must override this method.")
