"""Test cases for targeting solver function ."""

import lib.lib as lib
from os import path
from unittest import TestCase
import targeting_solver

class TestTargetingSolver(TestCase):

    """Test Targeting_Solver."""

    def setUp(self):
        self.config = lib.get_config()
        self.logger = lib.get_logger()
        self.logger.info("Running {}()".format(self._testMethodName))
        #config = path.dirname(path.realpath(__file__))+"/test_config.yaml"

    def test_getTargetDistance(self):
        distance = targeting_solver.getTargetDistance(.3572, 0.9144)
        self.assertAlmostEqual(distance, .95215)
