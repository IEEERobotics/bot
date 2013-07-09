#!/usr/bin/env python
"""Logic for line following."""

import lib.lib as lib


class Follower:

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build and store logger."""
        self.logger = lib.get_logger()
        self.logger.debug("Follower has logger")

    def follow(self, cmd):
        """Accept and handle fire commands.

        TODO(dfarrell07): This is a stub

        :param cmd: Description of fire action to execute.

        """
        self.logger.debug("Fire cmd: {}".format(cmd))
