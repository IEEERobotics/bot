"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi, fabs, sqrt

import driver
import lib.lib as lib
import hardware.motor as m_mod


class MecDriver(driver.Driver):

    """Subclass of Driver for movement with mecanum wheels."""

    def __init__(self):
        """Run superclass's init, build motor abstraction objects."""
        super(MecDriver, self).__init__()

        # Create motor objects
        self.motors = {}
        for motor in self.config["drive_motors"]:
            self.motors[motor["position"]] = m_mod.Motor(motor["PWM"],
                                                         motor["GPIO"])

    def __str__(self):
        """Show status of motors."""
        return "fr: {}, fl: {} br: {}, bl: {}".format(
                                                self.motors["front_right"],
                                                self.motors["front_left"],
                                                self.motors["back_right"],
                                                self.motors["back_left"])

    def rotate(self, magnatude, direction):
        """Rotate the robot.

        :param magnitude: Rotation speed as percentage of max.
        :param direction: Direction of rotation ("cw" or "ccw")

        """
        # Validate params
        assert direction == "cw" or direction == "ccw"
        assert 0 <= magnatude <= 100

        # Set motor direction, based on http://goo.gl/B1KEUV
        if direction == "cw":
            self.motors["front_right"].direction = "reverse"
            self.motors["back_left"].direction = "forward"
        else:
            self.motors["front_left"].direction = "reverse"
            self.motors["back_right"].direction = "forward"

        # Set motor speeds
        for key in self.motors.keys():
            self.motors[key] = magnatude

        self.logger.debug("Magnitude: {}, direction: {}".format(magnatude,
                                                               direction))

    def move(self, speed, angle):
        """Move holonomically without rotation.

        :param speed: Magnitude of robot's translation speed (% of max).
        :type speed: float
        :param angle: Angle of translation in degrees (90=left, 270=right).
        :type angle: float

        """
        # Validate params
        assert 0 <= speed <= 100
        assert 0 <= angle <= 360

        # Calculate motor speeds
        front_left = speed * sin(angle * pi / 180 + pi / 4)
        front_right = speed * cos(angle * pi / 180 + pi / 4)
        back_left = speed * cos(angle * pi / 180 + pi / 4)
        back_right = speed * sin(angle * pi / 180 + pi / 4)
        
        #find largest motor speed, use to normalize vectors and maintain maximum efficiency
        max = max([front_left,front_right,back_left,back_right])
        front_left = front_left / max * 100
        front_right = front_right / max * 100
        back_left = back_left / max * 100
        back_right = back_right / max * 100

        # Set motor directions
        self.motors["front_left"] = "forward" if front_left > 0 else "reverse"
        self.motors["front_right"] = "forward" if front_right > 0 else \
                                                                  "reverse"
        self.motors["back_left"] = "forward" if back_left > 0 else "reverse"
        self.motors["back_right"] = "forward" if back_right > 0 else "reverse"

        # Set motor speeds
        self.motors["front_left"] = fabs(front_left)
        self.motors["front_right"] = fabs(front_right)
        self.motors["back_left"] = fabs(back_left)
        self.motors["back_right"] = fabs(back_right)

        self.logger.debug("Speed: {}, angle: {}".format(speed, angle))
