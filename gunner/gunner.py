"""Handle aiming and firing darts."""

import lib.lib as lib
import hardware.turret as turret
import hardware.wheel_gun as wheel_gun
import hardware.ultrasonic as ultrasonic
import targeting_solver as targeting
import time

class Gunner(object):

    """Logic for aiming the turret and firing darts.

    Intended to be subclassed by specializations for different firing systems.

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
    def aim_turret(self, pitch, yaw):
        """Aim the robot's turret such that firing will be successful.

        :param pitch: Angle on pitch axis to set turret servo.
        :param yaw: Angle on yaw axis to set turret servo.

        """
        self.logger.debug("Aiming turret to (pitch: {}, yaw: {})".format(pitch, yaw))
        self.turret.pitch = pitch
        self.turret.yaw = yaw

    @lib.api_call
    def get_turret(self):
        return self.turret.pitch, self.turret.yaw

    def localize(self, dists):
        """Localize based on range measurement from center of bot"""
        # TODO: Handle skewed bot when not square to the course (e.g. on the arc line)
        x, y, theta = self.dumb_localize(dists)
        self.logger.debug("Localize calulcated pose as x:{}, y:{}, theta:{}".format
                    (x,y,theta))
        return x,y,theta

    def dumb_localize(self, dists):
        """Localize based on range measurement from center of bot"""

        x_pos = dists['left']
        y_pos = dists['front']
        theta = 0.0

        return x_pos, y_pos, theta

    @lib.api_call
    def fire(self):
        """Get location, aim turret, accelerate wheels and advance dart."""
        # Go ahead and spin up the gun, to get it to speed
        self.gun.wheel_power = 100

        self.logger.debug("Calling localize with ultrasonic distances")
        dists = self.ultrasonics.read_dists()
        x_pos, y_pos, theta = self.localize(dists)

        # calculate dart_velocity: roughtly 5-14 m/s
        dart_velocity = self.gun.dart_velocity

        self.logger.debug("Getting firing solution using dart_vel: %0.2f", dart_velocity)
        pitch, yaw = targeting.getFiringSolution(x_pos, y_pos, theta, dart_velocity)
        self.aim_turret(pitch, yaw)

        # Allow turrent time to move
        # TODO: make config param so we can zero during testing
        time.sleep(0.2)

        # Call CV to find left-right offset, calc server adjustment based on dist to target
        # opencv stuff => image offset
        self.logger.warning("OpenCV turret repositioning not implemented")
        targeting.getTargetDistance(x_pos, y_pos)

        # Actuate motor to push dart into spinning wheels
        self.logger.info("Firing dart")
        self.gun.fire()


###################  from wheel_gun
    def fire_burst(self, count=3, delay=2):
        """Fire a number of darts consecutively.

        :param count: Number of darts to fire.
        :type count: int
        :param delay: Delay in seconds between firing each dart.
        :type delay: float

        """
        if count <= 0:
            self.logger.warning("Invalid count: {}".format(count))
            return False

        if delay <= 0.0:
            self.logger.warning("Invalid delay: {}".format(delay))
            return False

        for i in xrange(count):
            self.fire.fire()
            time.sleep(delay)
        return True

