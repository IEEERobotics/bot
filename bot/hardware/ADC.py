"""Hardware abstraction for ADS7830 ADC"""

from i2c_device.i2c_device import I2CDevice

import bbb.pwm as pwm_mod
import bot.lib.lib as lib


class ADC(I2CDevice):
    def __init__(self):
            """Initialized I2C device"""
            self.logger = lib.get_logger()
            self.bot_config = lib.get_config()

            # Handle off-bone runs
            self.testing = self.bot_config["testing"]
            if self.bot_config["test_mode"]["ADC"]:
                self.logger.debug("Running in test mode")
            else:
                self.logger.debug("Running in non-test mode")

                # Setup I2C
                I2CDevice.__init__(self, 1, 0x12,
                                config='adc_ads7830_i2c.yaml')