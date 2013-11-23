"""Handle aiming and firing darts."""

import lib.lib as lib
import localizer.us_localizer as l_mod
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

        # Load and store configuration dict
        self.config = lib.get_config()

        # Load and store targeting dict
        self.targ = lib.load_targeting(self.config["targeting"])

        # Load and store ultrasonic localizer
        self.localizer = l_mod.USLocalizer()

        # Build turrent hardware abstraction
        self.turret = t_mod.Turret()

    def auto_fire(self):
        """Accept and handle fire commands.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        """
        self.logger.error("auto_fire method must be overridden by a subclass.")
        raise NotImplementedError("Subclass must override this method.")

    def aim_turret(self, yaw, pitch):
        """Aim the robot's turret such that firing will be successful.

        :param yaw: Angle on yaw axis to set turret servo.
        :param pitch: Angle on pitch axis to set turret servo.

        """
        try:
            assert 0 <= yaw <= 180
        except AssertionError:
            raise AssertionError("Yaw angle is out of bounds")
        try:
            assert 0 <= pitch <= 180
        except AssertionError:
            raise AssertionError("Pitch angle is out of bounds")

        self.logger.debug("Aiming turret to ({}, {})".format(yaw, pitch))
        self.turret.yaw = yaw
        self.turret.pitch = pitch
