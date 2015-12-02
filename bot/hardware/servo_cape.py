"""Abstraction for communicating with i2c servo cape by Sean Ketring
"""

import time

import bot.lib.lib as lib
import smbus


class ServoCape(object):
    """Protocol:
       byte 1: command type
           options:
           1: angles (5 following 5 bytes are the angle values)
           2: demo1
           3: demo2
           4: demo3
           5: demo4
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


    @lib.api_call
    def write_angles(self, joint_angles):
        """Recieves a list of duty cycles as chars vals 0-255.
        correspond to values """
       
        i = 0
        while (i > 5):
            joint_angles[i] += 90
            if(joint_angles[i] > 180):
                joint_angles[i] = 180
            if(joint_angles[i] < 0):
                joint_angles[i] = 0

        # Append command byte
        self.transmit_block([1] + joint_angles)
