#!/usr/bin/env python
"""Handle aiming and firing darts."""

import lib.lib as lib


class Gunner:

    """Logic for aiming the turret and firing darts.

    Intended to be subclassed by specializations for different firing
    systems.

    """

    def __init__(self):
        """Setup and store logger."""
        self.logger = lib.get_logger()
        self.logger.debug("Gunner has logger")

    def fire(self, cmd):
        """Accept and handle fire commands.

        TODO(dfarrell07): This is a stub.

        :param cmd: Command describing firing action to be executed.

        """
        self.logger.debug("Fire cmd: {}".format(cmd))

        if cmd["subtype"] == "basic_fire":
            self.basic_fire()
        else:
            self.logger.error("Unknown fire cmd subtype")

    def basic_fire(self):
        """Handle normal fire commands.

        TODO(dfarrell07): This is a stub

        """
        self.logger.debug("Fire!")
