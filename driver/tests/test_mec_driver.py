"""Test cases for mec driver."""
import sys
import os
import unittest
from math import fabs, hypot, atan2, degrees

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import driver.mec_driver as md_mod
    from driver.mec_driver import MecDriver  # for convenience
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise

# Logger object
logger = lib.get_logger()


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
        rotate_speed_error_margin = (MecDriver.max_rotate_speed -
                                     MecDriver.min_rotate_speed) * 0.05
        for test_rotate_speed in xrange(MecDriver.min_rotate_speed,
                                        MecDriver.max_rotate_speed + 1):
            # Issue rotate command
            logger.debug("Set rotate_speed: {}".format(test_rotate_speed))
            self.md.rotate(test_rotate_speed)
            logger.debug("Check rotate_speed: {}".format(self.md.rotate_speed))

            # Check for approximate speed, as float values will seldom be exact
            assert fabs(self.md.rotate_speed - test_rotate_speed) < \
                rotate_speed_error_margin

            # Check directions (skip if speed is too low)
            if fabs(test_rotate_speed) >= 10:
                assert self.md.motors["front_left"].direction == "reverse" if\
                    test_rotate_speed >= 0 else "forward"
                assert self.md.motors["front_right"].direction == "forward" if\
                    test_rotate_speed >= 0 else "reverse"
                assert self.md.motors["back_left"].direction == "reverse" if\
                    test_rotate_speed >= 0 else "forward"
                assert self.md.motors["back_right"].direction == "forward" if\
                    test_rotate_speed >= 0 else "reverse"

            # Check for valid duty cycles (speeds)
            for motor in self.md.motors.itervalues():
                assert MecDriver.min_speed <= motor.speed <= \
                    MecDriver.max_speed

    def test_move(self):
        speed_error_margin = (MecDriver.max_speed -
                              MecDriver.min_speed) * 0.05
        angle_error_margin = (MecDriver.max_angle -
                              MecDriver.min_angle) * 0.05
        for test_speed in xrange(MecDriver.min_speed + 1,
                                 MecDriver.max_speed + 1, 10):
            for test_angle in xrange(MecDriver.min_angle,
                                     MecDriver.max_angle + 1, 10):
                # Issue move command
                logger.debug("Set speed  : {:3d}, angle: {:3d}".format(
                    test_speed,
                    test_angle))
                self.md.move(test_speed, test_angle)
                logger.debug("Check speed: {:3d}, angle: {:3d}".format(
                    self.md.speed,
                    self.md.angle))

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
                        logger.debug(
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

    def test_move_forward_strafe(self):
        speed_error_margin = (MecDriver.max_speed -
                              MecDriver.min_speed) * 0.05
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
                logger.debug("Set forward: {:3d}, strafe: {:3d}".format(
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
                logger.debug("Exp. speed : {:3d}, angle: {:3d}".format(
                    test_speed,
                    test_angle))

                logger.debug("Check speed: {:3d}, angle: {:3d}".format(
                    self.md.speed,
                    self.md.angle))

                #Note: Speed no longer being checked due to
                #Normalization eqs changing it.

                if fabs(test_speed) >= 10:
                    assert fabs(self.md.angle - test_angle) % 360 < \
                        angle_error_margin

                # Check for valid duty cycles (speeds)
                for motor in self.md.motors.itervalues():
                    assert MecDriver.min_speed <= motor.speed <= \
                                                  MecDriver.max_speed
