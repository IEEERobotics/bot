#!/usr/bin/env python
"""Handle aiming and firing darts."""

import lib.lib as lib
import localizer.localizer as localizer


class Gunner(object):

    """Logic for aiming the turret and firing darts.

    Intended to be subclassed by specializations for different firing
    systems.

    """

    def __init__(self):
        """Setup and store logger and configuration."""
        # Load and store logger
        self.logger = lib.get_logger()
        self.logger.debug("Gunner has logger")

        # Load and store configuration dict
        self.config = lib.load_config()
        self.logger.debug("Gunner has config")

        # Load and store targeting dict
        self.targ = lib.load_targeting(self.config["targeting"])
        self.logger.debug("Targeting: {}".format(self.targ))

        # Load and store localizer
        self.localizer = localizer.Localizer()
        self.logger.debug("Gunner has localizer")

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

        This is designed to be overridden by more specific subclasses.

        TODO(dfarrell07): This is a stub

        """
        self.logger.debug("Fire!")

    def aim_turret(self):
        """Aim the robot's turret such that firing will be successful.

        TODO(dfarrell07): This is a stub

        """
        self.logger.debug("Aiming turret")
