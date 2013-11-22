"""Analog IR array abstractions."""

import ir


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
        # TODO: I2C setup code
        super(IRAnalog, self).__init__(name, read_gpio_pin)
