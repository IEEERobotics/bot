import time
from i2c_device.i2c_device import I2CDevice


class ColorSensor(I2CDevice):

    """Wrapper class for TCS3472 I2C-based color sensor."""

    # TODO: Make these config items and load in __init__()
    max_c = 65536

    #Base values to be changed by get_baseline
    bv = 0.0
    bc = 0.0
    bg = 0.0
    br = 0.0
    bb = 0.0

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
        enable.write('PON', 'Enable')
        print "Enabling ADCs via control register:"
        enable.write('AEN', 'Enable')

        #enable.write('PON','Disable')

        enable = self.registers['ENABLE']  # TODO: Is this needed?
        print "Register: ", enable
        print "Read: {:08b}".format(enable.read_byte())
        print

    @property
    def color(self):
        v, c, r, g, b = self.read_data()
        color = {"clear": c,
                  "red": r,
                  "green": g,
                  "blue": b}
        return color

    def get_data_normalized(self):
        valid, c, r, g, b = self.read_data()
        # NOTE: It appears that c = r + g + b
        # so 1/c is a good normalizing factor.
        # This ensures that normalized values indicate relative proportions.
        # We could also normalize each by a constant,
        # say, the max value (65535).
        c = float(c)

        r /= c
        g /= c
        b /= c
        c /= self.max_c  # normalize c to [0, 1] range
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
        # c = float(c)
        total = r + g + b
        r = (r/total)*100
        g = (g/total)*100
        b = (b/total)*100
        return v, c, r, g, b

    def get_baseline(self):
        """Obtains "base" colors to work from
        """
        self.bv, self.bc, \
        self.br, self.bg, \
        self.bb = self.read_data()

    def get_percent_diff(self):
        """Returns percent diff
        for use in color decisions.        
        """
        diff_c = (self.color["clear"] - self.bc)/self.bc
        diff_r = (self.color["red"] - self.br)/self.br
        diff_g = (self.color["green"] - self.bg)/self.bg
        diff_b = (self.color["blue"] - self.bb)/self.bb
        
        # diff_c = abs((self.color["clear"] - self.bc)/self.bc)*100
        # diff_r = abs((self.color["red"] - self.br)/self.br) * 100
        # diff_g = abs((self.color["green"] - self.bg)) * 100
        # diff_b = abs((self.color["blue"] - self.bb)/self.bb) *100

        return diff_c, diff_r, diff_g, diff_b

    def is_green_percent_method(self):
        """decides on color based on percentage
        """
        
        diff_c, diff_r, diff_g, diff_b = self.get_percent_diff()
        
        # returns true when g has greatest increase.
        if (diff_g > diff_r) & (diff_g > diff_b):
            return True
            
    def is_green_diff_method(self):
        """Decides on color based on difference in percentage 
        of total color increases by set amount.
        """
        
        # Reads in percentages of total color
        pv, pc, pr, pg, pb = colorSensor.get_percentage()
        
        total_color = self.color["red"] \
                    + self.color["green"] \
                    + self.color["blue"]
                    
        total_base = self.br + self.bg + self.bb

        # Base percentages for each color
        percent_baseb = self.br / total_base * 100
        percent_baseg = self.bg / total_base * 100
        percent_baseb = self.bb / total_base * 100
        
        # returns True when the percentage of a color goes up by 0.2 from base percents
        
        if (pg - percent_baseg) > 0.2:
            return True

        
        

    def is_green(self):
        """ finds percent difference between baseline
            and current reading.
        """
        diff_c, diff_r, diff_g, diff_b = self.get_percent_diff()
        
        print "diff_c", diff_c, "diff_r",diff_r, "diff_g",diff_g, "diff_b",diff_b 
        if (diff_g) > (diff_b + diff_r):
            return True

        
            
def read_loop():
    """Instantiate a ColorSensor object and read indefinitely."""
    print "start"
    colorSensor = ColorSensor()

    #gets base values for all colors.
    time.sleep(0.5)
    colorSensor.get_baseline()

    print "bv: {}, bc: {:5.3f}, br: {:5.3f}, bg: {:5.3f}, bb: {:5.3f}".format(colorSensor.bv, \
                                                                            colorSensor.bc,\
                                                                            colorSensor.br,\
                                                                            colorSensor.bg,\
                                                                            colorSensor.bb)


    # self.logger.debug("baseline: bv: {}, bc: {}, br: {}, bg: {}, bb: {}".format(bv, bc, br, bg, bb))

    print "before loop"
    t0 = time.time()
    while True:
        try:
            elapsed = time.time() - t0
            print "[{:8.3f}] ".format(elapsed),
            
            v, c, r, g, b = colorSensor.read_data()  # raw read
            
            # print "v: {}, c: {:5.3f}, r: {:5.3f}, g: {:5.3f}, b: {:5.3f}".format(v, c, r, g, b)
            print "bv: {}, bc: {:5.3f}, br: {:5.3f}, bg: {:5.3f}, bb: {:5.3f}".format(colorSensor.bv, \
                                                                        colorSensor.bc,\
                                                                        colorSensor.br,\
                                                                        colorSensor.bg,\
                                                                        colorSensor.bb)
            if colorSensor.is_green():
                print "Found green"
            #print "v: {}  c: {}, r: {}, g: {} b: {}".format(valid, c, r, g, b)
            # v, c, r, g, b = colorSensor.get_data_normalized()  # read normalized RGB values 
            #v, c, r, g, b = colorSensor.get_percentage()
            # Find out which color has plurality of percentage.
            # print "v: {}, c: {:5.3f}, r: {:5.3f}, g: {:5.3f}, b: {:5.3f}".format(v, c, r, g, b)
            
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    print "Done."

    


if __name__ == "__main__":
    read_loop()