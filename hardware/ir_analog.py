"""Analog IR array abstractions."""

import ir

i2c_available = False
try:
    import smbus
    i2c_available = True
except ImportError:
    print "ImportError: smbus module not found; I2C communication disabled"

def swap_bytes_uint16(value):
    """Swaps the bytes (endianness) of a 16-bit integer."""
    return ((value & 0x00ff) << 8) | ((value & 0xff00) >> 8)


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

        # ADC configuration over I2C
        adc_config = self.config['ir_analog_adc_config']
        self.i2c_addr = adc_config['i2c_addr'][name]
        if i2c_available:
            # Open I2C bus
            self.bus = smbus.SMBus(adc_config['i2c_bus'])

            # Configure ADC using I2C commands
            for reg_name, reg in adc_config['i2c_registers'].iteritems():
                if 'init' in reg and reg['init'] is not None:
                    if reg['bytes'] == 1:
                        self.bus.write_byte_data(self.i2c_addr,
                                                reg['addr'], reg['init'])
                    elif reg['bytes'] == 2:
                        # TODO: Check if we need to use swap_bytes_uint16()
                        self.bus.write_word_data(self.i2c_addr,
                                                reg['addr'], reg['init'])

            # Cache some config items that we may need later
            self.result_addr = adc_config['result_addr']  # 2 bytes
            self.result_mask = adc_config['result_mask']
            self.result_shift = adc_config['result_shift']
        self.logger.debug("Setup {} (on I2C addr: {})".format(self,
                                                        hex(self.i2c_addr)))

    def read_adc_result(self):
        if i2c_available:
            raw_result = swap_bytes_uint16(self.bus.read_word_data(
                                                        self.i2c_addr,
                                                        self.result_addr))
            # raw_result:- D15: alert; D14-D12, D3-D0: reserved; D11-D4: value
            result = (raw_result & self.result_mask) >> self.result_shift
            return result
        else:
            return 0
