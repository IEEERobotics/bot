#!/usr/bin/env python
"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi

import driver
import lib.lib as lib


class MechDriver(driver.Driver):

    """Subclass of Driver for movement with mecanum wheels.

    TODO(dfarrell07): Override Driver.move with translate + rotate combo code.

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
        :type ds: string
        :param ds: Duty cycle that motor should be set to.
        :type ds: float

        """
        self.logger.debug("IO write: motor: {}, ds: {}".format(motor, ds))

    def translate(self, speed, angle):
        """Calculate voltage multiplier for each motor, pass to IO pins.

        :param speed: Magnitude of robot's translation speed.
        :type speed: float
        :param angle: Angle in degrees at which robot should translate.
        :type angle: float

        """
        self.logger.debug("Translate speed: {}, angle: {}".format(speed, angle))

        # Calculate voltage multipliers
        front_left = speed * sin(angle*pi/180 + pi/4)
        front_right = speed * cos(angle*pi/ 180 + pi/4)
        back_left = speed * cos(angle*pi/ 180 + pi/4)
        back_right = speed * sin(angle*pi/180 + pi/4)

        # Write to IO pins.
        self.iowrite("front_left", front_left)
        self.iowrite("front_right", front_right)
        self.iowrite("back_left", back_left)
        self.iowrite("back_right", back_right)

    def rotate(self, rotate_speed):
        """Control rotation of robot.

        :param rotate_speed: Desired rotational speed.
        :type rotate_speed: float

        """
        self.logger.debug("Rotate speed: {}".format(rotate_speed))

        #Calculate voltage multipliers
        front_left = rotate_speed
        front_right = -rotate_speed
        back_left = rotate_speed
        back_right = -rotate_speed

        # Write to IO pins.
        self.iowrite("front_left", front_left)
        self.iowrite("front_right", front_right)
        self.iowrite("back_left", back_left)
        self.iowrite("back_right", back_right)
