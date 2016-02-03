"""Abstraction for communicating with i2c servo cape by Sean Ketring
"""

import time

import bot.lib.lib as lib
import smbus


class ServoCape(object):
    """Protocol:
    Cape expects to recieve a 6 byte array
    if the first byte is 0x00
        next 5 bytes are servo angles.
    otherwise the number of a demo.
    """

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
        else: 
            self.logger.debug("non test-mode, real hardware")

    @lib.api_call
    def transmit_block(self, array):
        try:
            self.bus.write_i2c_block_data(self.addr,
                                          self.reg,
                                          array)
        except IOError as err:
            self.logger.debug(err)
            return err


