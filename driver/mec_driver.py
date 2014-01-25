"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi, fabs, sqrt, hypot, atan2, degrees
from time import sleep, time
import driver
import lib.lib as lib
import hardware.motor as m_mod


class MecDriver(driver.Driver):
    """Subclass of Driver for movement with mecanum wheels."""
    # TODO: Check angle convention across class - math functions
    #   might be using counterclockwise positive

    min_speed = 0
    max_speed = 100
    min_angle = 0
    max_angle = 360
    min_rotate_speed = -100
    max_rotate_speed = 100

    #Used to keep track of last set speeds.
    translate_speed = 0
    translate_angle = 0
    rotate_speed = 0

    def __init__(self):
        """Run superclass's init, build motor abstraction objects."""
        super(MecDriver, self).__init__()

        # Create motor objects
        self.motors = {}
        for motor in self.config["drive_motors"]:
            self.motors[motor["position"]] = m_mod.Motor(motor["PWM"],
                                                         motor["GPIO"])

        # Reconfigure motors to account for opposite mounting directions
        #   between left and right side
        self.motors["front_right"].invert(True)
        self.motors["back_right"].invert(True)

    def __str__(self):
        """Show status of motors."""
        return "fr: {}, fl: {} br: {}, bl: {}".format(
            self.motors["front_right"],
            self.motors["front_left"],
            self.motors["back_right"],
            self.motors["back_left"])

    @property
    def speed(self):
        """Getter for bot's current overall speed as % of max
        (same as duty cycle).

        :returns: Current bot speed as percent of max real speed.

        """
        # Combine wheel velocity vectors, return magnitude
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV
        v_forward_right = self.motors["front_left"].velocity + \
            self.motors["back_right"].velocity
        v_forward_left = self.motors["front_right"].velocity + \
            self.motors["back_left"].velocity
        # TODO: Verify math; v/2 to take mean?
        return int(round(hypot(v_forward_right / 2, v_forward_left / 2)))

    @property
    def angle(self):
        """Getter for bot's current overall direction of movement.

        Combines wheel velocity vectors and returns angle (corrected
        to use forward as zero).

        :returns: Current bot angle in degrees.

        """
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV
        v_forward_right = self.motors["front_left"].velocity + \
            self.motors["back_right"].velocity
        v_forward_left = self.motors["front_right"].velocity + \
            self.motors["back_left"].velocity
        return int(round(
            degrees(atan2(v_forward_right, v_forward_left) - pi / 4))) % 360
        # TODO: Verify math; -pi/4 is because hypot will compute direction
        #   along forward_right diagonal
        # TODO: Correct this so that zero angle is returned
        #   (instead of -45) even when speed is near-zero

    @property
    def rotate_speed(self):
        """Getter for bot's current overall speed of rotation.

        :returns: Rotation speed in range [min_rotate_speed, max_rotate_speed].

        """
        # Return difference between left and right velocities
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV
        v_left = self.motors["front_left"].velocity + \
            self.motors["back_left"].velocity
        v_right = self.motors["front_right"].velocity + \
            self.motors["back_right"].velocity
        # TODO: Verify math; v/4 to take mean?
        return int(round((v_right - v_left) / 4))

    def rotate(self, rotate_speed):
        """Pass rotation speed as -100 to +100
        (positive is counterclockwise)."""

        # Validate params
        self.logger.debug("rotate_speed: {}".format(rotate_speed))
        try:
            assert MecDriver.min_rotate_speed <= rotate_speed <= \
                MecDriver.max_rotate_speed
        except AssertionError:
            raise AssertionError("Rotate speed is out of bounds")

        # Check for zero/near-zero speed
        if rotate_speed == 0:  # TODO deadband (epsilon) check?
            for motor in self.motors.itervalues():
                motor.speed = 0
            return

        # Set motor directions, based on http://goo.gl/B1KEUV
        # Also see MecanumWheelDirection.png
        # NOTE(napratin, 9/17): Only 2 wheels need to be turned on for each
        #   direction, as per diagram
        # NOTE(napratin, 9/17): But using all 4 wheels in a conventional
        #   differential drive configuration for rotation works fine
        if rotate_speed >= 0:
            # Counterclockwise
            self.motors["front_left"].direction = "reverse"
            self.motors["front_right"].direction = "forward"
            self.motors["back_left"].direction = "reverse"
            self.motors["back_right"].direction = "forward"
        else:
            # Clockwise
            self.motors["front_left"].direction = "forward"
            self.motors["front_right"].direction = "reverse"
            self.motors["back_left"].direction = "forward"
            self.motors["back_right"].direction = "reverse"

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
        self.logger.debug("speed: {}, angle: {}".format(speed, angle))
        try:
            assert MecDriver.min_speed <= speed <= MecDriver.max_speed
        except AssertionError:
            raise AssertionError("Speed is out of bounds")

        # Angle bounds may be unnecessary

        try:
            assert MecDriver.min_angle <= angle <= MecDriver.max_angle
        except AssertionError:
            raise AssertionError("Angle is out of bounds")

        # Handle zero speed, prevent divide-by-zero error
        if speed == 0:  # TODO deadband (epsilon) check?
            for motor in self.motors.itervalues():
                motor.speed = 0
            return

        # Calculate motor speeds
        # Formulae from Mecanumdrive.pdf in google drive.
        # TODO Check math: why are all the phase offsets +pi/4?
        front_left = speed * sin(angle * pi / 180 + pi / 4)
        front_right = speed * cos(angle * pi / 180 + pi / 4)
        back_left = speed * cos(angle * pi / 180 + pi / 4)
        back_right = speed * sin(angle * pi / 180 + pi / 4)
        self.logger.debug((
            "pre-scale : front_left: {:6.2f}, front_right: {:6.2f},"
            " back_left: {:6.2f}, back_right: {:6.2f}").format(
                front_left, front_right, back_left, back_right))

        # Find largest motor speed,
        # use that to normalize multipliers and maintain maximum efficiency
        # TODO This needs to be debugged and re-enabled; currently speeds are
        # being set much higher than expected (use test_mec_driver to verify)
        max_wheel_speed = max(
            [fabs(front_left), fabs(front_right),
                fabs(back_left), fabs(back_right)]
        )
        front_left = front_left * speed / max_wheel_speed
        front_right = front_right * speed / max_wheel_speed
        back_left = back_left * speed / max_wheel_speed
        back_right = back_right * speed / max_wheel_speed
        self.logger.debug(
            ("post-scale: front_left: {:6.2f}, front_right: {:6.2f},"
                " back_left: {:6.2f}, back_right: {:6.2f}").format(
                    front_left, front_right, back_left, back_right))

        # Set motor directions
        self.motors["front_left"].direction = "forward" if front_left >= 0 \
            else "reverse"
        self.motors["front_right"].direction = "forward" if front_right >= 0 \
            else "reverse"
        self.motors["back_left"].direction = "forward" if back_left >= 0 \
            else "reverse"
        self.motors["back_right"].direction = "forward" if back_right >= 0 \
            else "reverse"

        # Set motor speeds
        self.motors["front_left"].speed = fabs(front_left)
        self.motors["front_right"].speed = fabs(front_right)
        self.motors["back_left"].speed = fabs(back_left)
        self.motors["back_right"].speed = fabs(back_right)

    def move_forward_strafe(self, forward, strafe):
        # Scale down speed by sqrt(2) to make sure we're in range
        # NOTE(napratin, 9/27): Scaling down is not required since we clamp
        #   speed to [min, max] anyways
        speed = hypot(forward, strafe)  # / 1.414
        if speed < MecDriver.min_speed:
            speed = MecDriver.min_speed
        elif speed > MecDriver.max_speed:
            speed = MecDriver.max_speed
        # Note order of atan2() args to get forward = 0 deg
        angle = degrees(atan2(strafe, forward)) % 360
        self.move(speed, angle)

    def compound_move(self, translate_speed, translate_angle, rotate_speed):
        """Translate and move at same time.

        Note: I have no idea how to predict where the bot ends up
        during compound movement.

        speed, rotate_speed is number between 0, 100.
        """

        # Speeds should add up to max_speed (100)
        # TODO: Should this be fabs(rotate_speed)?
        total_speed = translate_speed + rotate_speed
        assert total_speed <= MecDriver.max_speed
        self.logger.debug("translate_speed: {}, " +
                          "translate_angle: {}, " +
                          "rotate_speed: {}".format(translate_speed,
                                                    translate_angle,
                                                    rotate_speed))

        # Calculate overall voltage multiplier
        front_left = translate_speed * sin(angle * pi / 180 + pi / 4) + \
            rotate_speed
        front_right = translate_speed * cos(angle * pi / 180 + pi / 4) - \
            rotate_speed
        back_left = translate_speed * cos(angle * pi / 180 + pi / 4) + \
            rotate_speed
        back_right = translate_speed * sin(angle * pi / 180 + pi / 4) - \
            rotate_speed

        # Normalize so that at least one wheel_speed equals maximum wheel_speed
        max_wheel_speed = max([
            fabs(front_left), fabs(front_right), fabs(back_left),
            fabs(back_right)
        ])
        front_left = front_left * translate_speed / max_wheel_speed
        front_right = front_right * translate_speed / max_wheel_speed
        back_left = back_left * translate_speed / max_wheel_speed
        back_right = back_right * translate_speed / max_wheel_speed

        # Set motor directions
        self.motors["front_left"].direction = "forward" if front_left > 0 \
            else "reverse"
        self.motors["front_right"].direction = "forward" if front_right > 0 \
            else "reverse"
        self.motors["back_left"].direction = "forward" if back_left > 0 \
            else "reverse"
        self.motors["back_right"].direction = "forward" if back_right > 0 \
            else "reverse"

        # Set motor speeds
        self.motors["front_left"].speed = fabs(front_left)
        self.motors["front_right"].speed = fabs(front_right)
        self.motors["back_left"].speed = fabs(back_left)
        self.motors["back_right"].speed = fabs(back_right)

    def jerk(self):
        """Makes small forward jump in position.
            """

        #Time and speed of jerk.
        jerk_time = 3
        jerk_speed = 30

        # Set motor to "speed"
        for motor in self.motors.itervalues():
            motor.speed = jerk_speed
            motor.direction = "forward"

        # Wait for "time" seconds
        sleep(jerk_time)

        # stop motors.
        for motor in self.motors.itervalues():
            motor.speed = 0

    def drive(self, translate_speed, translate_angle, time):
        """Moves in direction of translate angle at translate speed for set
            time (in seconds) and then stops.
           """

        move(translate_speed, translate_angle)
        sleep(time)
        move(0, 0)
