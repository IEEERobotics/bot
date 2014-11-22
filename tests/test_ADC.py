"""Test cases for the ADS7830 ADC. ""

import time
from unittest import TestCase, expectedFailure
import struct

import bot.lib.lib as lib
from i2c_device.i2c_device import I2CDevice
from bot.hardware.ADC import ADC

config_file = path.dirname(path.realpath(__file__))+"/test_config.yaml"
config = lib.get_config(config_file)

class TestADC(TestCase):
