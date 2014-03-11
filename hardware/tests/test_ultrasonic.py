"""Test cases for DMCC motor abstraction class."""

import lib.lib as lib
from os import path

config_file = path.dirname(path.realpath(__file__))+"/test_config.yaml"
config = lib.get_config(config_file)

import hardware.ultrasonic
from hardware.ultrasonic import Ultrasonic

from unittest import TestCase, expectedFailure
import struct

class TestUltrasonic(TestCase):

    """Test ultrasonic set."""

    def setUp(self):
        config_file = path.dirname(path.realpath(__file__))+"/test_config.yaml"
        lib.get_config(config_file)
        logger = lib.get_logger()
        logger.info("Using test config: {}".format(config_file))
        logger.info("Running {}()".format(self._testMethodName))

    def test_read(self):
        us = Ultrasonic()
        us.pru_mem = struct.pack('IIIIIIII', 1,2,3,4,5,6,7,8)
        inches = us.read_times()
        self.assertEqual(len(inches),4)
        self.assertEqual(inches['front'], 1)
        self.assertEqual(inches['back'], 3)
        self.assertEqual(inches['left'], 5)
        self.assertEqual(inches['right'], 7)

    def test_inches(self):
        us = Ultrasonic()
        us.pru_mem = struct.pack('IIIIIIII', 1,2,3,4,5,6,7,8)
        inches = us.read_inches()
        self.assertEqual(inches['back'], 3/149.3)
        self.assertEqual(inches['right'], 7/149.3)

    def test_dists(self):
        us = Ultrasonic()
        us.pru_mem = struct.pack('IIIIIIII', 1,2,3,4,5,6,7,8)
        dists = us.read_dists()
        self.assertEqual(dists['back'], 3/149.3 + 0.15)
