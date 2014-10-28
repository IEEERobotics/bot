"""Test cases for targeting solver function ."""

import lib.lib as lib
from os import path
from unittest import TestCase
import gunner.targeting_solver as targeting

class TestTargetingSolver(TestCase):

    """Test Targeting_Solver."""

    def setUp(self):
        self.config = lib.get_config()
        self.logger = lib.get_logger()
        self.logger.info("Running {}()".format(self._testMethodName))
        #config = path.dirname(path.realpath(__file__))+"/test_config.yaml"

    def test_getTargetDistance(self):
        distance = targeting.getTargetDistance(.3572, 0.9144)
        self.assertAlmostEqual(distance, .9422, places=4)

    def test_getHorizLaunchAngle(self):
        deflectionAngle = targeting.getHorizLaunchAngle(.3572, 0.9144)
        self.assertAlmostEqual(deflectionAngle, 13.942, places=2)

    def test_getMinElevationAngle(self):
        minElevAngle = targeting.getMinElevationAngle(.9422)
        self.assertAlmostEqual(minElevAngle, 22.186, places=2)

    def test_getServoAngle(self):
        servoAngle = targeting.getServoAngle(26)
        self.assertAlmostEqual(servoAngle, 57.66, places=2)

    def test_getFiringSolution(self):
        vert_servo_angle, horiz_servo_angle = targeting.getFiringSolution(.3572,.9144, 0, 7.4439)
        self.assertAlmostEqual(horiz_servo_angle, 13.942, places=2)
        self.assertAlmostEqual(vert_servo_angle, 63, places=0)

    def test_getFiringSolution_bad_velocity(self):
        with self.assertRaises(ValueError):
            targeting.getFiringSolution(.3572,.9144, 0, .5)
