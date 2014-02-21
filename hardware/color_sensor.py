import time
from i2c_device.i2c_device import I2CDevice

class ColorSensor(I2CDevice):
    """Wrapper class for TCS3472 I2C-based color sensor."""

    # TODO: Make these config items and load in __init__()
    max_c = 65536

    def __init__(self):
        I2CDevice.__init__(self, 1, 0x29, config='tcs3472_i2c.yaml')

        # TODO: Instantiate GPIO pin for LED control
        # TODO: Convert all print stmts. to logger.debug() calls
        print "ColorSensor:", self
        print

        enable = self.registers['ENABLE']
        print "Register: ", enable
        print "Raw: {:08b}".format(enable.read_byte())
        print "AEN: {}".format(enable.read('AEN'))
        print

        id = self.registers['ID']
        print "Register: ", id
        print "Read: {:#010x}".format(id.read_byte())
        print

        status = self.registers['STATUS']
        print "Register: ", status
        print "Raw: {:08b}".format(status.read_byte())
        print "AVALID: {}".format(status.read('AVALID'))

        print "Enabling power via control register:"
        enable.write('PON','Enable')
        print "Enabling ADCs via control register:"
        enable.write('AEN','Enable')

        #enable.write('PON','Disable')

        enable = self.registers['ENABLE']  # TODO: Is this needed?
        print "Register: ", enable
        print "Read: {:08b}".format(enable.read_byte())
        print

    def get_data_normalized(self):
        valid, c, r, g, b = self.read_data()
        # NOTE: It appears that c = r + g + b, so 1/c is a good normalizing factor.
        #       This ensures that normalized values indicate relative proportions.
        #       We could also normalize each by a constant, say, the max value (65535).
        c = float(c)
        c /= self.max_c #normalize to 0-1
        r /= c
        g /= c
        b /= c
        #c /= self.max_c  # normalize c to [0, 1] range
        return valid, c, r, g, b  # return valid flag if someone's interested

    def read_data(self):
        valid = self.registers['STATUS'].read('AVALID')
        c = self.registers['CDATA'].read()
        r = self.registers['RDATA'].read()
        g = self.registers['GDATA'].read()
        b = self.registers['BDATA'].read()
        return valid, c, r, g, b
        
    def get_percentage(self):
        """ Returns what portion of detected color is 
        """
        v, c, r, g, b = self.get_data_normalized()
        c = float(c)
        r = (r/c)*100
        g = (r/g)*100
        b = (r/b)*100
        

    def get_baseline(self):
        v, c, r, g, b = self.get_data_normalized()
        return v, c, r, g, b

def read_loop():
    """Instantiate a ColorSensor object and read indefinitely."""
    colorSensor = ColorSensor()
    t0 = time.time()
    while True:
        try:
            elapsed = time.time() - t0
            print "[{:8.3f}] ".format(elapsed),
            #valid, c, r, g, b = colorSensor.read_data()  # raw read
            #print "v: {}  c: {}, r: {}, g: {} b: {}".format(valid, c, r, g, b)
            # v, c, r, g, b = colorSensor.get_data_normalized()  # read normalized RGB values 
            print "v: {}, c: {:5.3f}, r: {:5.3f}, g: {:5.3f}, b: {:5.3f}".format(v, c, r, g, b)
            
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    print "Done."


if __name__ == "__main__":
    read_loop()
