"""Handle aiming and firing darts."""

import lib.lib as lib
import hardware.turret as turret
import hardware.wheel_gun as wheel_gun
import hardware.ultrasonic as ultrasonic
import targeting_solver as targeting
import time
from math import acos, degrees

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
        x, y, theta = self.ratio_localizer(dists)
        self.logger.info("Localize calculated pose: ({}, {}, {})".format(
                    x, y, theta))
        return x,y,theta

    def dumb_localizer(self, dists_from_center):
        """Localize based on range measurement from center of bot, assuming square"""

        self.logger.warning("Using dumb localizer!")
        x = dists_from_center['back']
        y = dists_from_center['left']
        theta = 0.0
        self.logger.debug("Calculated pose: ({}, {}, {})".format(x,y,theta))
        return x, y, theta

    def ratio_localizer(self, dists_from_center):
        """Localize based on range measurement from center of bot"""

        x_size = self.config['course']['default']['x_size']
        y_size = self.config['course']['default']['y_size']

        # bot will have left side facing target
        # back + front = x_size when square
        # NOTE: right sensor may be unreliable since it encouters the +x wall

        dists = dists_from_center
        x_tot = dists['back'] + dists['front']
        ratio = x_size / x_tot
        self.logger.debug("Ratio: {:0.3f}".format(ratio))
        x_pos = dists['back'] * ratio
        y_pos = dists['left'] * ratio
        if ratio > 1.1:
            # TODO: use longer sensor + front as alternate?
            self.logger.error("Sensor X total ({}) MUCH smaller than course X ({})".format(x_tot, x_size))
            raise ValueError
        if ratio > 1:
            self.logger.warning("Sensor X total ({}) smaller than course X ({}), assuming square".format(x_tot, x_size))
            theta = 0.0
        else:
            # sin theta = (x_pos/back) = ratio
            theta = degrees(acos(ratio))

        # since the arc is well devined, assume we're always facing inward
        if x_pos < (x_size/2.0):
            theta = -theta

        self.logger.debug("Calculated pose: ({}, {}, {})".format(x_pos,y_pos,theta))

        return x_pos, y_pos, theta


    def validate_pose(self, x_pos, y_pos, theta):

        # minimums and maximums of possible blue block centers
        conf = self.config['course']['firing_box']
        y_min = conf['y_min']
        y_max = conf['y_max']
        x_min = conf['x_min']
        x_max = conf['x_max']
        if not ((x_min < x_pos < x_max) and (y_min < y_pos < y_max)):
            self.logger.warning("Invalid position for firing ({},{}), expected ({},{})-({},{})".format(
                    x_pos, y_pos, x_min, y_min, x_max, y_max))
            return False
            logger.debug("Position is valid for firing")
        return True

    @lib.api_call
    def aim(self):
        """Get location, aim turret, accelerate wheels and advance dart."""

        # We need to be up to speed before reading the dart velocity
        self.gun.spin_up()
        time.sleep(1.0)

        x_pos, y_pos, theta = self.localize()
        if not self.validate_pose(x_pos, y_pos, theta):
            self.logger.error("What do I do now?!")

        # dart_velocity should be roughtly 5-14 m/s
        dart_velocity = self.gun.dart_velocity

        self.logger.debug("Getting firing solution using dart_vel: %0.2f", dart_velocity)
        pitch, yaw = targeting.getFiringSolution(x_pos, y_pos, theta, dart_velocity)
        yaw += 90
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

