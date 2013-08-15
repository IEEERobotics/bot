#!/usr/bin/env python
import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import hardware.motor as m_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()

class TestSpeed(unittest.TestCase):

    def setUp(self):
        logger.debug("In setUp")
        self.motor = m_mod.Motor(0, testing=True)
        logger.debug("Built {}".format(self.motor))

    def test_off(self):
        self.motor.speed = 0
        print "In test_off"
