"""Handle aiming and firing darts."""

import lib.lib as lib
import hardware.turret as t_mod
import targeting_solver as targeter


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

        # Build turrent hardware abstraction
        self.turret = t_mod.Turret()

    def auto_fire(self):
        """Accept and handle fire commands.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        """
        self.logger.error("auto_fire method must be overridden by a subclass.")
        raise NotImplementedError("Subclass must override this method.")

    @lib.api_call
    def calc_pitch(self, x_pos, y_pos):
        """TODO: Clean up"""
        angle = targeter.getFiringSolution(x_pos, y_pos)
        pitch_angle = targeter.getServoAngle(angle)
        return pitch_angle
    
    @lib.api_call
    def calc_yaw(self, x_pos, y_pos):
        """TODO: Clean up"""
        yaw_angle = targeter.getHorizLaunchAngle(x_pos, y_pos) + 90
        return yaw_angle
    
    @lib.api_call
    def aim_turret(self, yaw, pitch):
        """Aim the robot's turret such that firing will be successful.

        :param yaw: Angle on yaw axis to set turret servo.
        :param pitch: Angle on pitch axis to set turret servo.

        """
        self.logger.debug("Aiming turret to ({}, {})".format(yaw, pitch))
        self.turret.yaw = yaw
        self.turret.pitch = pitch
