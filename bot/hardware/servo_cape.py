"""Abstraction for communicating with i2c servo cape by Sean Ketring
"""

import time

import bot.lib.lib as lib
import smbus


class ServoCape(object):

    def __init__(self, cape_config):
        """Initialize vars"""

        self.logger = lib.get_logger()
        self.bot_config = lib.get_config()

        self.bus  = smbus.SMBus(self.bot_config["dagu_arm"]["servo_cape"]["i2c_bus"])
        self.addr = self.bot_config["dagu_arm"]["servo_cape"]["i2c_addr"]
        #TODO(Ahmed): Figure out how to use regs
        self.reg = 0xFF

        if self.bot_config["test_mode"]["servo_cape"]:
            self.logger.debug("running in test mode")
        else 
            self.logger.debug("non test-mode, real hardware")

    @lib.api_call
    def write_angles(self, joint_angles):
        """Recieves a list of duty cycles as chars vals 0-255.
        correspond to values """
        try:
            self.bus.write_i2c_block_data(self.address, self.reg, joint_angles)
        except IOError as err:
        return self.errMsg()
