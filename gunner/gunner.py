"""Handle aiming and firing darts."""

import lib.lib as lib
import hardware.turret as turret
import hardware.wheel_gun as wheel_gun
import hardware.ultrasonic as ultrasonic
import targeting_solver as targeting
import time

class Gunner(object):

    """Logic for aiming the turret and firing darts.

    """

    def __init__(self):
        """Setup and store logger and configuration."""
        # Load and store logger
        self.logger = lib.get_logger()

        # Load and store configuration dict
        self.config = lib.get_config()

        self.gun = wheel_gun.WheelGun()
        self.turret = turret.Turret()
        self.ultrasonics = ultrasonic.Ultrasonic()


    @lib.api_call
    def localize(self):
        """Localize using ultrasonic sensors"""
        dists = self.ultrasonics.read_dists()
        # TODO: Handle skewed bot when not square to the course (e.g. on the arc line)
        x, y, theta = self.dumb_localizer(dists)
        self.logger.info("Localize calculated pose: ({}, {}, {})".format(
                    x, y, theta))
        return x,y,theta

    def dumb_localizer(self, dists_from_center):
        """Localize based on range measurement from center of bot"""

        self.logger.warning("Using dumb localizer!")
        x = dists_from_center['left']
        y = dists_from_center['front']
        theta = 0.0

        return x, y, theta

    @lib.api_call
    def aim(self):
        """Get location, aim turret, accelerate wheels and advance dart."""

        # We need to be up to speed before reading the dart velocity
        self.gun.spin_up()
        time.sleep(0.1)

        x_pos, y_pos, theta = self.localize()

        # dart_velocity should be roughtly 5-14 m/s
        dart_velocity = self.gun.dart_velocity

        self.logger.debug("Getting firing solution using dart_vel: %0.2f", dart_velocity)
        pitch, yaw = targeting.getFiringSolution(x_pos, y_pos, theta, dart_velocity)
        self.logger.info("Aiming turret to (pitch: {}, yaw: {})".format(pitch, yaw))
        self.turret.pitch = pitch
        self.turret.yaw = yaw

        # Allow turrent time to move
        # TODO: make config param so we can zero during testing
        time.sleep(0.2)

        # Call CV to find left-right offset, calc server adjustment based on dist to target
        # opencv stuff => image offset
        self.logger.warning("OpenCV turret repositioning not implemented")
        targeting.getTargetDistance(x_pos, y_pos)

    @lib.api_call
    def fire(self):
        """Tell the gun to fire a dart"""
        self.gun.fire()

