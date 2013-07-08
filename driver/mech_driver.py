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

    def basic_move(self, speed, angle, rotate_speed):
        """Build low-level commands for holonomic translations with rotations.

        :param speed: Magnitude of robot's translation speed.
        :type speed: float
        :param angle: Angle in degrees at which robot should translate.
        :type angle: float
        :param rotate_speed: Desired rotational speed.
        :type rotate_speed: float

        """
        self.logger.debug("Speed: {}, angle {}, rotate speed {}".format(speed,
                                                            angle,
                                                            rotate_speed))

        # Calculate voltage multipliers
        front_left_ds = speed * sin(angle*pi/180 + pi/4) + rotate_speed
        front_right_ds = speed * cos(angle*pi/ 180 + pi/4) - rotate_speed
        back_left_ds = speed * cos(angle*pi/ 180 + pi/4) + rotate_speed
        back_right_ds = speed * sin(angle*pi/180 + pi/4) - rotate_speed

        # Write to IO pins.
        self.iowrite("front_left", front_left_ds)
        self.iowrite("front_right", front_right_ds)
        self.iowrite("back_left", back_left_ds)
        self.iowrite("back_right", back_right_ds)
