"""Hardware abstraction for ADS7830 ADC"""

import time
import smbus as bus

from i2c_device.i2c_device import I2CDevice

import bbb.pwm as pwm_mod
import bot.lib.lib as lib



class ADC(object):
    def __init__(self):
            """Initialized I2C device"""
            self.logger = lib.get_logger()
            self.bot_config = lib.get_config()
            
            # Default value of command byte. 
            # Refer to ADS_7830 for more information
            
            # Handle off-bone runs
            if self.bot_config["test_mode"]["ADC"]:
                self.logger.debug("Running in test mode")
            else:
                self.logger.debug("Running in non-test mode")

                # Setup I2C
                addr = self.bot_config
                I2CDevice.__init__(self, 1, 0x48,
                                config='adc_ads7830_i2c.yaml')

    @lib.api_call
    def read_channel(self, channel_num, SD=0b0,
                    internal_ref=0b0, AD_converter=0b0):
        # Append bits to form command byte.
        command_byte = (SD << 7) | (channel_num << 4) \
                       (internal_ref << 3) | (AD_converter << 2) \
                       | (0b00)
        bus.write_byte(self.addr, command_byte)
        return bus.read_byte(self.addr)

    @lib.api_call
    def read_all(self)
        return read_channel(0), read_channel(1), read_channel(2), \
               read_channel(3), read_channel(4), read_channel(5), \
               read_channel(6), read_channel(7)

    @lib.api_call
    def print_all(self)
        print "0:{} 1:{} 2:{} 3:{} 4:{} 5:{} 6:{} 7:{}".format(
                                            self.read_all())
                                            
    @lib.api_call
    def read_loop(self)
        t0 = time.time()
        while True:
            try:
                print "[{:8.3f}] ".format(time.time()-t0),
                self.print_all()
            except KeyboardInterrupt:
                break
        print "Done."