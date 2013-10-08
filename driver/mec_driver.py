"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi, fabs, sqrt, hypot, atan2, degrees

import driver
import lib.lib as lib
import hardware.motor as m_mod


class MecDriver(driver.Driver):
    """Subclass of Driver for movement with mecanum wheels."""
    # TODO check angle convention across class - math functions might be using counterclockwise positive

    min_speed = 0
    max_speed = 100
    min_angle = 0
    max_angle = 360
    min_rotate_speed = -100
    max_rotate_speed = 100

    def __init__(self):
        """Run superclass's init, build motor abstraction objects."""
        super(MecDriver, self).__init__()

        # Create motor objects
        self.motors = {}
        for motor in self.config["drive_motors"]:
            self.motors[motor["position"]] = m_mod.Motor(motor["PWM"],
                                                         motor["GPIO"])

    @property
    def speed(self):
        """Getter for bot's current overall speed as % of max (same as duty cycle).
        :returns: Current bot speed as percent of max real speed.
        """
        # Combine wheel velocity vectors, return magnitude
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV
        v_forward_right = self.motors["front_left"].velocity + self.motors["back_right"].velocity
        v_forward_left = self.motors["front_right"].velocity + self.motors["back_left"].velocity
        return int(round(hypot(v_forward_right / 2, v_forward_left / 2)))  # TODO verify math; v/2 to take mean?

    @property
    def angle(self):
        """Getter for bot's current overall direction of movement.
        :returns: Current bot angle in degrees.
        """
        # Combine wheel velocity vectors, return angle (corrected to use forward as zero)
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV
        v_forward_right = self.motors["front_left"].velocity + self.motors["back_right"].velocity
        v_forward_left = self.motors["front_right"].velocity + self.motors["back_left"].velocity
        return int(round(degrees(atan2(v_forward_right, v_forward_left) - pi / 4))) % 360  # TODO verify math; -pi/4 is because hypot will compute direction along forward_right diagonal
        # TODO correct this so that zero angle is returned (instead of -45) even when speed is near-zero

    @property
    def rotate_speed(self):
        """Getter for bot's current overall speed of rotation.
        :returns: Current bot rotation speed in range [min_rotate_speed, max_rotate_speed].
        """
        # Return difference between left and right velocities
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV
        v_left = self.motors["front_left"].velocity + self.motors["back_left"].velocity
        v_right = self.motors["front_right"].velocity + self.motors["back_right"].velocity
        return int(round((v_left - v_right) / 4))  # TODO verify math; v/4 to take mean?

    def __str__(self):
        """Show status of motors."""
        return "fr: {}, fl: {} br: {}, bl: {}".format(self.motors["front_right"],
                                                      self.motors["front_left"],
                                                      self.motors["back_right"],
                                                      self.motors["back_left"])

    def rotate(self, rotate_speed):
        """Pass rotation speed as -100 to +100 (positive is clockwise)."""
        # Validate params
        assert MecDriver.min_rotate_speed <= rotate_speed <= MecDriver.max_rotate_speed
        self.logger.debug("rotate_speed: {}".format(rotate_speed))

        # Check for zero/near-zero speed
        if rotate_speed == 0:  # TODO deadband (epsilon) check?
            for motor in self.motors.itervalues():
                motor.speed = 0
            return

        # Set motor directions, based on http://goo.gl/B1KEUV
        # Also see MecanumWheelDirection.png
        if rotate_speed >= 0:
            self.motors["front_left"].direction = "forward"
            self.motors["front_right"].direction = "reverse"
            self.motors["back_left"].direction = "forward"
            self.motors["back_right"].direction = "reverse"
        else:
            self.motors["front_left"].direction = "reverse"
            self.motors["front_right"].direction = "forward"
            self.motors["back_left"].direction = "reverse"
            self.motors["back_right"].direction = "forward"

        # Set motor speeds
        abs_speed = fabs(rotate_speed)
        for motor in self.motors.itervalues():
            motor.speed = abs_speed

    def move(self, speed, angle):
        """Move holonomically without rotation.

        :param speed: Magnitude of robot's translation speed (% of max).
        :type speed: float
        :param angle: Angle of translation in degrees (90=left, 270=right).
        :type angle: float
        """
        # Validate params
        assert MecDriver.min_speed <= speed <= MecDriver.max_speed
        assert MecDriver.min_angle <= angle <= MecDriver.max_angle
        self.logger.debug("speed: {}, angle: {}".format(speed, angle))

        # Handle zero speed, prevent divide-by-zero error
        if speed == 0:  # TODO deadband (epsilon) check?
            for motor in self.motors.itervalues():
                motor.speed = 0
            return

        # Calculate motor speeds
        # Formulae source found in http://goo.gl/rrxDex
        front_left = speed * sin(angle * pi / 180 + pi / 4)
        front_right = speed * cos(angle * pi / 180 + pi / 4)
        back_left = speed * cos(angle * pi / 180 + pi / 4)
        back_right = speed * sin(angle * pi / 180 + pi / 4)

        # Find largest motor speed,
        # use that to normalize multipliers and maintain maximum efficiency
        # TODO This needs to be debugged and re-enabled; currently speeds are being set much higher than expected (use test_mec_driver to verify)
        '''
        max_wheel_speed = max([front_left, front_right, back_left, back_right])
        front_left = front_left * speed / max_wheel_speed
        front_right = front_right * speed / max_wheel_speed
        back_left = back_left * speed / max_wheel_speed
        back_right = back_right * speed / max_wheel_speed
        '''

        # Set motor directions
        self.motors["front_left"].direction = "forward" if front_left > 0 else "reverse"
        self.motors["front_right"].direction = "forward" if front_right > 0 else "reverse"
        self.motors["back_left"].direction = "forward" if back_left > 0 else "reverse"
        self.motors["back_right"].direction = "forward" if back_right > 0 else "reverse"

        # Set motor speeds
        self.motors["front_left"].speed = fabs(front_left)
        self.motors["front_right"].speed = fabs(front_right)
        self.motors["back_left"].speed = fabs(back_left)
        self.motors["back_right"].speed = fabs(back_right)

    def move_forward_strafe(self, forward, strafe):
        speed = hypot(forward, strafe) / 1.414  # scale down speed by sqrt(2) to make sure we're in range
        if speed < MecDriver.min_speed:
            speed = MecDriver.min_speed
        elif speed > MecDriver.max_speed:
            speed = MecDriver.max_speed
        angle = degrees(atan2(forward, strafe)) % 360  # note order of atan2() args to get forward = 0 deg
        self.move(speed, angle)

    def compound_move(self, translate_speed, translate_angle, rotate_speed):
        """Translate and move at same time.
            Note: I have no idea how to predict where the bot ends up
            during compound movement.
            speed, rotate_speed is number between 0, 100.
        """

        # Speeds should add up to max. speed (100)
        total_speed = fabs(translate_speed) + fabs(rotate_speed)
        assert total_speed <= MecDriver.max_speed

        self.logger.debug("translate_speed: {}, translate_angle: {}, rotate_speed: {}".format(translate_speed, translate_angle, rotate_speed))

        # Calculate overall voltage multiplier
        front_left = translate_speed * sin(angle * pi / 180 + pi / 4) + rotate_speed
        front_right = translate_speed * cos(angle * pi / 180 + pi / 4) - rotate_speed
        back_left = translate_speed * cos(angle * pi / 180 + pi / 4) + rotate_speed
        back_right = translate_speed * sin(angle * pi / 180 + pi / 4) - rotate_speed

        # Normalize so that at least one wheel_speed equals maximum wheel_speed
        max_wheel_speed = max([front_left, front_right, back_left, back_right])
        front_left = front_left / max_wheel_speed * total_speed
        front_right = front_right / max_wheel_speed * total_speed
        back_left = back_left / max_wheel_speed * total_speed
        back_right = back_right / max_wheel_speed * total_speed

        # Set motor directions
        self.motors["front_left"].direction = "forward" if front_left > 0 else "reverse"
        self.motors["front_right"].direction = "forward" if front_right > 0 else "reverse"
        self.motors["back_left"].direction = "forward" if back_left > 0 else "reverse"
        self.motors["back_right"].direction = "forward" if back_right > 0 else "reverse"

        # Set motor speeds
        self.motors["front_left"].speed = fabs(front_left)
        self.motors["front_right"].speed = fabs(front_right)
        self.motors["back_left"].speed = fabs(back_left)
        self.motors["back_right"].speed = fabs(back_right)

    def jerk(self, cmd):
        """Move forward for a certain amount of time or distance"""

    def oscilate(self):
        """Move oscillate sideways, increasing amplitude until a line is found"""
