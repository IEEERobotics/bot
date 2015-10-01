"""Test cases for mec driver."""

from math import fabs, hypot, atan2, degrees
from unittest import expectedFailure

from bot.driver.mec_driver import MecDriver  # For convenience
import tests.test_bot as test_bot


class TestRotate(test_bot.TestBot):
    """Test rotation of mec wheels"""

    def setUp(self):
        """Setup test hardware files and create mec_driver object"""
        # Run general bot test setup
        super(TestRotate, self).setUp()

        # Build mec_driver
        self.md = MecDriver()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestRotate, self).tearDown()

    def test_rotate(self):
        self.logger.info("Running test_rotate()")
        angular_rate_error_margin = (MecDriver.max_angular_rate -
                                     MecDriver.min_angular_rate) * 0.05
        for test_angular_rate in xrange(MecDriver.min_angular_rate,
                                        MecDriver.max_angular_rate + 1):
            # Issue rotate command
            self.md.rotate(test_angular_rate)

            # Check for approximate speed, as float values will seldom be exact
            self.logger.debug("md.ang_vel: {:3d}, test_ang_vel: {:3d}".format(
                self.md.rotation_rate, test_angular_rate))
            assert fabs(self.md.rotation_rate - test_angular_rate) < \
                angular_rate_error_margin

    @expectedFailure
    # FIXME: direction no longer exists as an attribute
    def test_rotate_motor_dirs(self):
        for test_angular_rate in xrange(MecDriver.min_angular_rate,
                                        MecDriver.max_angular_rate + 1):

            # Check directions (skip if speed is too low)
            if fabs(test_angular_rate) >= 10:
                assert self.md.motors["front_left"].direction == "reverse" if\
                    test_angular_rate >= 0 else "forward"
                assert self.md.motors["front_right"].direction == "forward" if\
                    test_angular_rate >= 0 else "reverse"
                assert self.md.motors["back_left"].direction == "reverse" if\
                    test_angular_rate >= 0 else "forward"
                assert self.md.motors["back_right"].direction == "forward" if\
                    test_angular_rate >= 0 else "reverse"

    def test_rotate_motor_vals(self):
        for test_angular_rate in xrange(MecDriver.min_angular_rate,
                                        MecDriver.max_angular_rate + 1):
            # Check for valid duty cycles (speeds)
            for motor in self.md.motors.itervalues():
                assert MecDriver.min_speed <= motor.speed <= \
                    MecDriver.max_speed

    def test_move(self):
        angle_error_margin = (MecDriver.max_angle -
                              MecDriver.min_angle) * 0.05
        for test_speed in xrange(MecDriver.min_speed + 1,
                                 MecDriver.max_speed + 1, 10):
            for test_angle in xrange(MecDriver.min_angle,
                                     MecDriver.max_angle + 1, 10):
                # Issue move command
                self.logger.debug("Set speed  : {:3d}, angle: {:3d}".format(
                    test_speed, test_angle))
                self.md.move(test_speed, test_angle)
                self.logger.debug("Check speed: {:3d}, angle: {:3d}".format(
                    self.md.speed, self.md.angle))

                """
                Commented out due to normalizing ruining proportions.
                Re-activate if we ever remove that.
                # Check for approximate match, floats will seldom be exact
                assert fabs(self.md.speed - test_speed) < speed_error_margin
                """

                # NOTE(napratin, 11/1): speed will mismatch if there's scaling
                # Don't check angle if speed is too low
                if fabs(test_speed) >= 10:
                    assert fabs(self.md.angle - test_angle) % 360 < \
                        angle_error_margin
                # Check for positive values when bot moving forward.
                if test_angle == 0:
                    for position, motor in self.md.motors.iteritems():
                        self.logger.debug(
                            "Ahmed Motor: {}, Speed: {}, Motor_speed:" +
                            "{}, Angle: {}, Direction: {}".format(
                                position,
                                test_speed,
                                motor.speed,
                                test_angle,
                                motor.direction
                            ))
                        assert motor.direction == "forward"

                # Check for valid duty cycles (speeds)
                for motor in self.md.motors.itervalues():
                    assert MecDriver.min_speed <= motor.speed <= \
                        MecDriver.max_speed

    def test_move_zero(self):
        self.logger.info("Running test_move_zero()")
        self.logger.debug("Setting to zero")
        self.md.move(0, 0)
        self.assertEqual(self.md.speed, 0)
        self.logger.debug("Setting to 50")
        self.md.move(50, 0)
        self.assertNotEqual(self.md.speed, 0)
        self.logger.debug("Setting to zero again")
        self.md.move(0, 0)
        self.assertEqual(self.md.speed, 0)
        self.logger.debug("Setting to zero with angle")
        self.md.move(0, 90)
        self.assertEqual(self.md.speed, 0)

    def test_move_forward_strafe(self):
        angle_error_margin = (MecDriver.max_angle -
                              MecDriver.min_angle) * 0.05

        for test_forward in xrange(
            MecDriver.min_speed + 1,
            MecDriver.max_speed + 1, 10
        ):
            for test_strafe in xrange(
                MecDriver.min_speed,
                MecDriver.max_speed + 1, 10
            ):
                # Issue move_forward_strafe command
                self.logger.debug("Set forward: {:3d}, strafe: {:3d}".format(
                    test_forward,
                    test_strafe))
                self.md.move_forward_strafe(test_forward, test_strafe)

                # Compute expected speed and angle
                test_speed = int(hypot(test_forward, test_strafe))
                if test_speed < MecDriver.min_speed:
                    test_speed = MecDriver.min_speed
                elif test_speed > MecDriver.max_speed:
                    test_speed = MecDriver.max_speed
                # Note order of atan2() args to get forward = 0 deg
                test_angle = int(degrees(atan2(test_strafe, test_forward))) \
                    % 360
                self.logger.debug("Exp. speed : {:3d}, angle: {:3d}".format(
                    test_speed, test_angle))

                self.logger.debug("Check speed: {:3d}, angle: {:3d}".format(
                    self.md.speed, self.md.angle))

                # Note: Speed no longer being checked due to
                # Normalization eqs changing it.

                if fabs(test_speed) >= 10:
                    assert fabs(self.md.angle - test_angle) % 360 < \
                        angle_error_margin

                # Check for valid duty cycles (speeds)
                for motor in self.md.motors.itervalues():
                    assert MecDriver.min_speed <= motor.speed <= \
                        MecDriver.max_speed

    def test_compound_move(self):
        # FIXME: This is just a dumb function that calls compound_move()
        #        It does not verify if the motor powers set are correct.
        # FIXME: Determinea and break this into qualitative test cases

        # Issue compound_move command
        translate_speed = 75
        translate_angle = 45
        angular_rate = 50
        self.logger.debug(
            "Set speed: {:3d}, angle: {:3d}, ""rate: {:3d}".format(
                translate_speed, translate_angle, angular_rate))
        self.md.compound_move(
            translate_speed, translate_angle, angular_rate)
        self.logger.debug(
            "Check speed: {:3d}, angle: {:3d}".format(
                self.md.speed, self.md.angle))

        # Check for valid duty cycles (speeds)
        for motor in self.md.motors.itervalues():
            assert MecDriver.min_speed <= motor.speed
            assert motor.speed <= MecDriver.max_speed
