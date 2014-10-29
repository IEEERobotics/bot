"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi, fabs, sqrt, hypot, atan2, degrees
from time import sleep, time

import bot.driver.driver as driver
import bot.lib.lib as lib
from bot.hardware.dmcc_motor import DMCCMotorSet


class MecDriver(driver.Driver):
    """Subclass of Driver for movement with mecanum wheels."""
    # TODO: Check angle convention across class - math functions
    #   might be using counterclockwise positive

    min_speed = 0
    max_speed = 100
    min_angle = -360
    max_angle = 360
    min_angular_rate = -100
    max_angular_rate = 100

    #Used to keep track of last set speeds.
    #translate_speed = 0
    #translate_angle = 0
    #angular_rate = 0

    def __init__(self, mode = 'power'):
        """Run superclass's init, build motor abstraction objects."""
        super(MecDriver, self).__init__()

        # Create motor objects
        motor_config = self.config['dmcc_drive_motors']
        self.motors = DMCCMotorSet(motor_config)
        self.mode = mode

    def __str__(self):
        """Show status of motors."""
        return "fr: {}, fl: {} br: {}, bl: {}".format(
            self.motors["front_right"],
            self.motors["front_left"],
            self.motors["back_right"],
            self.motors["back_left"])

    def get_motor(self, name):
        if self.mode == 'power':
            return self.motors[name].power
        else:
            return self.motors[name].velocity

    def set_motor(self, name, value):
        if self.mode == 'power':
            self.motors[name].power = value
        else:
            self.motors[name].velocity = value

    @property
    def speed(self):
        """Getter for bot's current overall speed as % of max
        (same as duty cycle).

        :returns: Current bot speed as percent of max real speed.

        """
        # Combine wheel velocity vectors, return magnitude
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV

        v_forward_right = self.get_motor("front_left") + \
            self.get_motor("back_right")
        v_forward_left = self.get_motor("front_right") + \
            self.get_motor("back_left")
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
        v_forward_right = self.get_motor("front_left") + \
            self.get_motor("back_right")
        v_forward_left = self.get_motor("front_right") + \
            self.get_motor("back_left")
        return int(round(
            degrees(atan2(v_forward_right, v_forward_left) - pi / 4))) % 360
        # TODO: Verify math; -pi/4 is because hypot will compute direction
        #   along forward_right diagonal
        # TODO: Correct this so that zero angle is returned
        #   (instead of -45) even when speed is near-zero

    @lib.api_call
    def get_rotation(self):
        """Getter for bot's current overall speed of rotation.

        :returns: Rotation speed in [min_angular_rate max_angular_rate].

        """
        # Return difference between left and right velocities
        # Note: Mecannum wheels must be oriented as per http://goo.gl/B1KEUV
        v_left = self.get_motor("front_left") + \
            self.get_motor("back_left")
        v_right = self.get_motor("front_right") + \
            self.get_motor("back_right")
        rotation =  int(round((v_right - v_left) / 4))
        self.logger.debug("Rotation:  (left {}: right: {})".format(rotation, v_left, v_right))
        # TODO: Verify math; v/4 to take mean?
        return rotation

    rotation_rate = property(get_rotation)

    @lib.api_call
    def rotate(self, rate):
        """Pass (angular) rate as -100 to +100
        (positive is counterclockwise)."""

        # Validate params
        self.logger.debug("Rotating with angular rate: {}".format(rate))
        try:
            assert MecDriver.min_angular_rate <= rate <= \
                MecDriver.max_angular_rate
        except AssertionError:
            raise AssertionError("Angular rate is out of bounds")

        #if rate == 0:  # TODO deadband (epsilon) check?

        self.set_motor("front_left", -rate)
        self.set_motor("front_right", rate)
        self.set_motor("back_left", -rate)
        self.set_motor("back_right", rate)

        # NOTE(napratin, 9/17):
        # Set motor directions, based on http://goo.gl/B1KEUV
        # Also see MecanumWheelDirection.png
        # Only 2 wheels need to be turned on for each direction, but using all
        # 4 wheels in a conventional differential
        # rotation works fine


    @lib.api_call
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
            self.logger.debug("Special case for speed == 0")
            self.set_motor("front_left", 0)
            self.set_motor("front_right", 0)
            self.set_motor("back_left", 0)
            self.set_motor("back_right", 0)
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

        # Set motor speeds
        self.set_motor("front_left", front_left)
        self.set_motor("front_right", front_right)
        self.set_motor("back_left", back_left)
        self.set_motor("back_right", back_right)

    @lib.api_call
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

    @lib.api_call
    def compound_move(self, translate_speed, translate_angle, angular_rate):
        """Translate and move at same time.

        Note: I have no idea how to predict where the bot ends up
        during compound movement.

        speed is number between 0, 100.
        angular_rate is number between -100, 100.
        TODO(napratin, 2/28): Check angular_rate range.
        """

        # Speeds should add up to max_speed (100)
        # TODO: Should this be fabs(rotate_speed)?
        total_speed = translate_speed + angular_rate
        if total_speed > MecDriver.max_speed:
            self.logger.warn("Total speed of move exceeds max: {}/{}".format(
                total_speed, MecDriver.max_speed))

        self.logger.debug("translate_speed: {}, " +
                          "translate_angle: {}, " +
                          "angular_rate: {}".format(translate_speed,
                                                    translate_angle,
                                                    angular_rate))

        # Calculate overall voltage multiplier
        front_left = translate_speed * \
            sin(translate_angle * pi / 180 + pi / 4) + angular_rate
        front_right = translate_speed * \
            cos(translate_angle * pi / 180 + pi / 4) - angular_rate
        back_left = translate_speed * \
            cos(translate_angle * pi / 180 + pi / 4) + angular_rate
        back_right = translate_speed * \
            sin(translate_angle * pi / 180 + pi / 4) - angular_rate

        # Find largest motor speed,
        # use that to normalize multipliers and maintain maximum efficiency
        max_wheel_speed = max(
            [fabs(front_left), fabs(front_right),
                fabs(back_left), fabs(back_right)]
        )
        
        total_speed = translate_speed + angular_rate

        front_left = front_left * total_speed / max_wheel_speed
        front_right = front_right * total_speed / max_wheel_speed
        back_left = back_left * total_speed / max_wheel_speed
        back_right = back_right * total_speed / max_wheel_speed

        self.logger.debug(
            ("post-scale: front_left: {:6.2f}, front_right: {:6.2f},"
                " back_left: {:6.2f}, back_right: {:6.2f}").format(
                    front_left, front_right, back_left, back_right))

        # Set motor speeds
        self.set_motor("front_left", front_left)
        self.set_motor("front_right", front_right)
        self.set_motor("back_left", back_left)
        self.set_motor("back_right", back_right)

    @lib.api_call
    def drive(self, speed, angle, duration):
        """Moves at given speed and angle for set duration (in seconds)."""
        self.move(speed, angle)  # start moving
        sleep(duration)  # wait for desired duration (in seconds)
        self.move(0, 0)  # stop

    @lib.api_call
    def jerk(self, speed=80, angle=0, duration=.25):
        """Makes small forward jump - a thin wrapper over drive()."""
        self.drive(speed, angle, duration)
