#!/usr/bin/env python
"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi
from time import sleep

import driver
import lib.lib as lib


class MechDriver(driver.Driver):

    """Subclass of Driver for movement with mecanum wheels.

    Motor A = front left
    Motor B = front Right
    Motor C = Back Left
    Motor D = Back Right

    """

    def __init__(self):
        """Setup logger."""

        self.logger = lib.get_logger()
        self.logger.debug("MechDriver has logger")

    def iowrite(self, motor, ds):
        """Write to IO pens that control the motors.

        TODO(dfarrell07): This is a stub

        :param motor: Motor to set speed of.
        :param ds: Duty cycle that motor should be set to.

        """
        self.logger.debug("IO write: motor: {}, ds: {}".format(motor, ds))

    def move(self, speed, angle, time=0):
        """Calculate voltage multiplier for each motor, pass to io pins.

        :param speed: Magnitude of robot's translation speed.
        :type speed: float
        :param angle: Angle in degrees at which robot should translate.
        :type angle: float
        :param time: Time in seconds that robot should do this move.
        :type time: float

        """
        # Calculate voltage multipliers
        front_left = speed * sin(angle*pi/180 + pi/4)
        front_right = speed * cos(angle*pi/ 180 + pi/4)
        back_left = speed * cos(angle*pi/ 180 + pi/4)
        back_right = speed * sin(angle*pi/180 + pi/4)

        # Write to io pins.
        iowrite("front_left", front_left)
        iowrite("front_right", front_right)
        iowrite("back_left", back_left)
        iowrite("back_right", back_right)

        # Sleep for user defined amount of time
        sleep(time)

        # Stop robot movement.
        iowrite("front_left", 0)
        iowrite("front_right", 0)
        iowrite("back_left", 0)
        iowrite("back_right", 0)

    def rotate(self, Rspeed, time=None):
        """Control rotation of robot.

        Note that the time param is designed for testing, especially
        via the CLI, as it may be difficult to fire a move and stop command
        as quickly as would be desired.

        :param Rspeed: Desired rotational speed.
        :param time: Number of seconds to force rotation.

        """
        #Calculate voltage multipliers
        front_left = Rspeed
        front_right = -Rspeed
        back_left = Rspeed
        back_right = -Rspeed

        # Write to io pins.
        iowrite("front_left", front_left)
        iowrite("front_right", front_right)
        iowrite("back_left", back_left)
        iowrite("back_right", back_right)

        # Sleep for user defined amount of time
        if time is not None:
            sleep(time)

        # Stop robot movement.
        iowrite("front_left", 0)
        iowrite("front_right", 0)
        iowrite("back_left", 0)
        iowrite("back_right", 0)
