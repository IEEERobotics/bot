"""Test cases for the ADS7830 ADC. """

import time
from unittest import TestCase, expectedFailure
import struct
import os

import bot.lib.lib as lib
import bot.hardware.ADC as adc_mod

config_file = os.path.dirname(os.path.realpath(__file__))+"/test_config.yaml"
config = lib.get_config(config_file)

class TestADC(test_bot.TestBot):

    """Test set up and read values of external ADC's."""

    def setUp(self):
        """Setup test IR_board for reading generic values from ADC"""
        
        # General test bot setup
        super(TestADC, self).setUp()

        # Create test-ADC's using fake i2c address.
        self.adc_addresses = self.config['IR_board']

        # Build set of ADC's from set of addresses.
        self.adc_list = dict()
        for address in self.adc_addresses:
            adc_list.append(adc_mod.ADC(1, address))

    def tearDown(self):
        """Restore previous test flag state."""
        super(TestADC, self).tearDown()

    def test_read(self):
        """Tests reading of all adc's"""

        # Read every adc.
        for adc in self.adc_list:
            # Read all channels
            for chan in range(0,7):
                adc.read_channel(chan)
