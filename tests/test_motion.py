"""Test cases for physical bot motion using motors."""

import unittest
import time

import lib.lib as lib
import hardware.motor as m_mod

# Build logger
logger = lib.get_logger()


class TestMotion(unittest.TestCase):
    """Test different motion patterns."""

    def setUp(self):
        """Create motor objects and set initial state to 0 speed."""
        # NOTE: Not setting testing flag to True here since we are
        #   using physical motors

        # Load config, get logger
        self.config = lib.get_config()

        # Create motor objects to test
        self.num_motors = 4
        self.drive_motors = [None] * self.num_motors
        for i in xrange(self.num_motors):
            self.drive_motors[i] = m_mod.Motor(
                                   self.config['drive_motors'][i]['PWM'],
                                   self.config['drive_motors'][i]['GPIO'])

        # NOTE: 0 = front_right, 1 = front_left, 2 = back_left, 3 = back_right

        # Set initial speeds to zero
        self.stop()

    def tearDown(self):
        # Set speeds back to zero
        self.stop()

    def do_forward(self):
        logger.info("Testing forward motion")
        self.move([1, 1, 0, 0], [50, 50, 50, 50])
        time.sleep(2)
        self.stop()

    def do_backward(self):
        logger.info("Testing backward motion")
        self.move([0, 0, 1, 1], [50, 50, 50, 50])
        time.sleep(2)
        self.stop()

    def do_forward_backward(self):
        logger.info("Testing forward and backward motion")
        self.do_forward()
        self.do_backward()

    def do_strafe(self, direction=0):
        logger.info("Testing strafe motion with dir = {}".format(direction))
        self.move([direction, 1 - direction, 1 - direction, direction],
                  [50, 50, 50, 50])
        time.sleep(1)
        self.stop()

    def do_dance(self):
        logger.info("Testing repeated strafe motion")
        for i in xrange(5):
            self.do_strafe(0)
            self.do_strafe(1)

    def move(self, directions, speeds):
        # dirs and speeds must be the same length as self.drive_motors
        assert len(self.drive_motors) == len(directions) == len(speeds)
        tuples = zip(self.drive_motors, directions, speeds)
        for motor, direction, speed in tuples:
            if motor is None:
                continue
            motor.direction = direction
            motor.speed = speed

    def stop(self):
        for motor in self.drive_motors:
            if motor is None:
                continue
            motor.speed = 0
