"""Abstraction of turret hardware."""

import lib.lib as lib
import hardware.servo as servo

class Turret(object):

    """Abstract x and y servos into a turret."""

    def __init__(self):
        """Load logger and build x and y servo abstractions."""
        # Load and store logger object
        self.logger = lib.get_logger()

        # Build and store abstraction of servos for x and y axis movement
        self.servo_x = servo.Servo(0)
        self.servo_y = servo.Servo(1)

    def __str__(self):
        """Represent turret in a human-readable way."""
        return "Turret: servo_x: {}, servo_y: {}".format(self.servo_x, 
                                                         self.servo_y)

    @property
    def x_angle(self):
        """Getter for position in degrees of turret on x-axis.

        :returns: Angle in degrees of turret on x-axis.

        """
        return self.servo_x.position

    @x_angle.setter
    def x_angle(self, angle):
        """Setter for position of turret on x-axis.

        :param angle: Angle in degrees to set turret to on x-axis.

        """
        self.servo_x.position = angle

    @property
    def y_angle(self):
        """Getter for position in degrees of turret on y-axis.

        :returns: Angle in degrees of turret on y-axis.

        """
        return self.servo_y.position

    @y_angle.setter
    def y_angle(self, angle):
        """Setter for position of turret on y-axis.

        :param angle: Angle in degrees to set turret to on y-axis.

        """
        self.servo_y.position = angle
