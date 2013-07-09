#!/usr/bin/env python
"""Module for handling high-level movement commands."""
import lib.lib as lib


class Driver(object):

    """Handle high-level movement commands."""

    def __init__(self):
        """Setup and store logger and config."""

        self.logger = lib.get_logger()
        self.logger.debug("Driver has logger")

        self.config = lib.get_config()
        self.logger.debug("Driver has config")

    def move(self, desc):
        """Accept and handle a movement command.

        TODO(dfarrell07): This is a stub.

        :param desc: Description of movement command to handle.
        :type desc: string

        """
        self.logger.debug("Mv cmd: {}".format(desc))
