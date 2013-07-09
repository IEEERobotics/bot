#!/usr/bin/env python
"""Handle aiming and firing darts."""

try:
    import yaml
except ImportError, err:
    sys.stderr.write("ERROR: {}. Try installing python-yaml.\n".format(err))

import lib.lib as lib


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
        self.config = lib.get_config()
        self.logger.debug("Gunner has config")

        # Load and store targeting dict
        self.targ = self.load_targeting()
        self.logger.debug("Targeting: {}".format(self.targ))

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

    def load_targeting(self):
        """Load the YAML targeting info for each possible block position.

        :returns: Dict description of targeting information for each block.

        """
        # Build valid path from CWD to targeting file
        qual_targ_file = lib.prepend_prefix(self.config["targeting"])
        self.logger.debug("Targeting file: " + qual_targ_file)

        # Open and read targeting file
        targ_fd = open(qual_targ_file)
        return yaml.load(targ_fd)
