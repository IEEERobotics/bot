"""Abstraction for communicating with i2c servo cape by Sean Ketring
"""

import time

import bot.lib.lib as lib
import smbus


class servo_cape(object):
    """init device"""
    self.logger = lib.get_logger()
    self.bot_config = lib.get_config()


    def __init__(self, i2c_bus, i2c_address):
        """Initialize vars"""

        self.logger = lib.get_logger()
        self.bot_config = lib.get_config()

        self.bus_num = i2c_bus

        self.bus  = SMBus(self.bus_num)
        self.addr = i2c_address
        #TODO(Ahmed): Figure out how to use regs
        self.reg = 123

        if self.bot_config["test_mode"]["servo_cape"]:
            self.logger.debug("running in test mode")
        else 
            self.logger.debug("non test-mode, real hardware")

    @lib.api_call
    def set_duty_cycles(self, joint_angles):
        """Recieves set of duty cycles as chars vals 0-255.
        correspond to values """

        #TODO(Ahmed) find way to write all angles at once.
        for angle in joint_angles:
            bus.write_byte(self.addr, angle)
            time.sleep(0.1)
