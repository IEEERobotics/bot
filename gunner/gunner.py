"""Handle aiming and firing darts."""

import lib.lib as lib
import localizer.localizer as l_mod
import hardware.turret as t_mod


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
        self.localizer = l_mod.Localizer()
        self.logger.debug("Gunner has localizer")

        # Build turrent hardware abstraction
        self.turret = t_mod.Turret()
        self.logger.debug("Gunner has turret")

    def fire(self, cmd):
        """Accept and handle fire commands.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        :param cmd: Command describing firing action to be executed.

        """
        self.logger.error("The fire method must be overridden by a subclass.")
        raise NotImplementedError("Subclass must override this method.")

    def aim_turret(self, x_angle, y_angle):
        """Aim the robot's turret such that firing will be successful.

        :param x_angle: Angle on X axis to set turret servo.
        :param y_angle: Angle on Y axis to set turret servo.

        """
        self.logger.debug("Aiming turret to ({}, {})".format(x_angle, y_angle))
        self.turret.x_angle = x_angle
        self.turret.y_angle = y_angle
