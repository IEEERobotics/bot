"""Analog IR array abstractions."""

import ir

i2c_available = False
try:
    import smbus
    i2c_available = True
except ImportError:
    print "ImportError: smbus module not found; I2C communication disabled"


class IRAnalog(ir.IRArray):
    """Abstraction for analog IR arrays.

    There are two 8-unit IR arrays on each of the four sides of the bot,
    which are abstracted in hardware into a 16 unit array. There are
    currently two types of arrays, one digital and one analog. This is
    the class for abstracting analog arrays.

    """

    def __init__(self, name, read_gpio_pin):
        """Setup required pins and get logger/config.

        Note that the value read on the read_gpio_pin will depend on
        the currently value on the GPIO select lines. IRHub manages
        the iteration over the select lines and the reading of each
        array's read_gpio at each step of the iteration.

        The analog array's hardware requires some configuration via
        I2C before it can be used. We don't currently know how that
        works, so for now we'll assume its GPIOs are ready to read.

        :param name: Identifier for this IR array.
        :type name: string
        :param read_gpio_pin: Pin used by array to read an IR unit.
        :type input_adc_pin: int

        """
        super(IRAnalog, self).__init__(name, read_gpio_pin)
        
        # ADC configuration code (I2C)
        # TODO: Generalize this for different ADCs
        if i2c_available:
            self.bus1 = smbus.SMBus(1)
            self.bus1.write_byte_data(0x50, 0x02, 0x2d)
            self.bus1.write_word_data(0x50, 0x03, 0x0000)
            self.bus1.write_word_data(0x50, 0x04, 0x0750)
            self.bus1.write_word_data(0x50, 0x05, 0x0080)

    def read_accurate_value(self):
        if i2c_available:
            raw_value = self.bus1.read_word_data(0x50, 0x00)
            # raw_value:- D15: alert; D14-D12, D3-D0: reserved; D11-D4: value
            byte_value = int("{:16b}".format(value)[4:-4], 2)  # bits D11-D14
            inv_value = byte_value ^ 0xff  # invert it
            return inv_value
        else:
            return 0
