"""Analog IR array abstractions."""

import bot.lib.lib as lib

i2c_available = False
try:
    import smbus
    from time import sleep
    i2c_available = True
except ImportError:
    print "ImportError: smbus module not found; I2C communication disabled"

# TODO: Try using read_i2c_block_data() and write_i2c_block_data() instead?


def swap_bytes_uint16(value):
    """Swaps the bytes (endianness) of a 16-bit integer."""
    return ((value & 0x00ff) << 8) | ((value & 0xff00) >> 8)


class Pot(object):
    """Abstraction for potentiometer on the sensor board

    There is one Pot on the sensor cap. The pot is 
    accessed through the i2c bus 2. The i2c Address
    is located in the dic.
    """

    def __init__(self, name, color_detectors):
        """Setup required pins and get logger/config.

        :param name: Identifier for this pot.
        :type name: string
        :param color_detectors: Pin used by the detection circuit.
        :type input_adc_pin: int

        """


        self.name = name
        self.logger = lib.get_logger()
        self.config = lib.get_config()

        # ADC configuration over I2C
        self.pot_config = self.config['pot_config']
        self.i2c_addr = self.pot_config['i2c_addr'][name]
        self.color_gpio = self.config["simon"]["colors"]
        self.color_detectors = color_detectors

        if i2c_available:
            # Open I2C bus
            self.bus = smbus.SMBus(self.pot_config['i2c_bus'])

            # Configure ADC using I2C commands
            for reg_name, reg in self.pot_config['i2c_registers'].iteritems():
                self.set_pot_byte(reg['cmd'], reg['init'])

        self.logger.debug("Setup {} (on I2C addr: {})".format(
            self, hex(self.i2c_addr)))

    def set_pot_byte(self, register, byte_value):
        self.bus.write_byte_data(self.i2c_addr, register, byte_value)

    def write_pot_byte(self, byte_value):
        self.bus.write_byte(self.i2c_addr, byte_value)

    def read_pot_byte(self):
        return self.bus.read_byte(self.i2c_addr)

    def get_byte(self,value):
        #self.write_adc_byte(value)
        return self.bus.read_byte_data(self.i2c_addr,value)     #self.read_adc_byte()

    def set_pot_word(self, register, word_value):
        # TODO: Check if we need to use swap_bytes_uint16()
        self.bus.write_word_data(self.i2c_addr, register, word_value)

    def read_pot_result(self):
        """This is on Follower's critical path. Keep it fast."""
        if i2c_available:
            raw_result = swap_bytes_uint16(
                self.bus.read_word_data(
                    self.i2c_addr, self.result_addr))
            # raw_result:- D15: alert; D14-D12, D3-D0: reserved; D11-D4: value
            result = (raw_result & self.result_mask) >> self.result_shift
            return result
        else:
            return 0

    @lib.api_call
    def set_pot_wiper(self, pot_name, pot_value): 
        """This Function is used to change the resisance value of the pot""" 

        reg_config = self.pot_config["i2c_registers"][pot_name] 
        self.set_pot_byte(reg_config["cmd"],pot_value)


    @lib.api_call
    def find_ambient_light(self): 
        """This Function is used to adjust the pot to the ambient light""" 
        
        # Set all pots to a max value    
        self.set_pot_wiper("yellow",511)
        self.set_pot_wiper("red",511)
        self.set_pot_wiper("blue",511)
        self.set_pot_wiper("green",511)
        
        # Create a dic for storing the max value
        thresh_value = {'green': 511, 'red': 511, 'yellow': 511, 'blue': 511}

        # Loop trough the pots and decrease the resistances if the sensor  
        for i in range(255, 40, -5):
            for color in self.color_gpio:
                if self.color_detectors[color].get_value() == 1:
                    self.set_pot_wiper(color,i)
                    thresh_value[color] = i

        # Adjust for maren
        for color in self.color_gpio:
            self.set_pot_wiper(color,thresh_value[color]-20)
            print "wiper set to {} for {}".format(thresh_value[color],color)
            print "gpio {} is {}".format(color, self.color_detectors[color].get_value())


