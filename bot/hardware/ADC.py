"""Hardware abstraction for ADS7830 ADC"""

from i2c_device.i2c_device import I2CDevice

import bbb.pwm as pwm_mod
import bot.lib.lib as lib


class ADC(I2CDevice):
