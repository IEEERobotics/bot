#!/usr/bin/env python
"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi

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

    def move(self, speed, angle):
        """Calculate voltage multiplier for each motor, pass to io pins.

        :param speed: Magnitude of robot's translation speed.
        :type speed: float
        :param angle: Angle in degrees at which robot should translate.
        :type angle: float

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

    def rotate(self, Rspeed):
        """Control rotation of robot.

        :param Rspeed: Desired rotational speed.

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
