"""Hardware abstraction for ADS7830 ADC"""

import time
import bot.lib.lib as lib


class ADC(object):

    """Class for communicating with ADS_7830 external ADC's"""

    def __init__(self, i2c_bus, i2c_address):
        """Initialized I2C device"""
        self.logger = lib.get_logger()
        self.bot_config = lib.get_config()

        # Bus location and address of ADC.
        self.bus = i2c_bus
        self.addr = i2c_address

        # Handle off-bone runs
        if self.bot_config["test_mode"]["ADC"]:
            self.logger.debug("Running in test mode")
        else:
            self.logger.debug("Running in non-test mode")

    @lib.api_call
    def read_channel(self, channel_num, SD=0b0,
                     internal_ref=0b0, AD_converter=0b0):
        """Reads channel specified by channel_num, with options.

        :param channel_num: Channel 0-7 of analog input to read.
        :type channel_num: int

        """
        # Append bits to form command byte.
        command_byte = (SD << 7) | (channel_num << 4)\
            | (internal_ref << 3) | (AD_converter << 2)\
            | (0b00)
        self.bus.write_byte(self.addr, command_byte)
        return self.bus.read_byte(self.addr)

    @lib.api_call
    def read_all(self):
        return self.read_channel(0), self.read_channel(1), self.read_channel(2), \
            self.read_channel(3), self.read_channel(4), self.read_channel(5), \
            self.read_channel(6), self.read_channel(7)

    @lib.api_call
    def print_all(self):
        print "0:{} 1:{} 2:{} 3:{} 4:{} 5:{} 6:{} 7:{}".format(
            self.read_all())

    @lib.api_call
    def read_loop(self):
        t0 = time.time()
        while True:
            try:
                print "[{:8.3f}] ".format(time.time() - t0),
                self.print_all()
            except KeyboardInterrupt:
                break
        print "Done."
