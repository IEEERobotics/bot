"""Controls activity related to RGB color sensor."""
import time

import pybbb.bbb.pwm as pwm_mod
from i2c_device.i2c_device import I2CDevice
import lib.lib as lib


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
        """Initialized I2C device, LED brightness PWM pin."""
        I2CDevice.__init__(self, 1, 0x29, config='tcs3472_i2c.yaml')
        enable = self.registers['ENABLE']
        id = self.registers['ID']
        status = self.registers['STATUS']
        enable.write('PON', 'Enable')
        enable.write('AEN', 'Enable')
        enable = self.registers['ENABLE']  # TODO: Is this needed?

        self.logger = lib.get_logger()
        self.config = lib.get_config()

        self.pwm_num = self.config["color_sensor"]["LED_PWM"]
        self.pwm = pwm_mod.PWM(self.pwm_num)
        # Duty cycle = 50% (from 20msec)
        self.pwm.duty = 1000000

    @property
    def color(self):
        """Actual color currently being viewed.
        
        :returns: dict containing color components.
        
        """
        v, c, r, g, b = self.read_data()
        color = {"clear": c,
                  "red": r,
                  "green": g,
                  "blue": b}
        return color

    def get_data_normalized(self):
        """Finds normalized color readings, compared to overall color viewing.
        
        :returns: Validity, Clear (magnitude), red, green, blue

        """
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
        """Reads in raw data directly from color_sensor.
        
        :returns: Validity, Clear (magnitude), Red, Green, Blue.
        
        """
        valid = self.registers['STATUS'].read('AVALID')
        c = self.registers['CDATA'].read()
        r = self.registers['RDATA'].read()
        g = self.registers['GDATA'].read()
        b = self.registers['BDATA'].read()
        return valid, c, r, g, b

    def get_percentage(self):
        """Calculates percentages of total color for each color.
        
        :returns: Validity, Clear (magnitude), Red, Green, Blue.

        """
        v, c, r, g, b = self.get_data_normalized()
        total = r + g + b
        r = (r / total) * 100
        g = (g / total) * 100
        b = (b / total) * 100
        return v, c, r, g, b

    def get_baseline(self):
        """Obtains "base" colors to work from.

        :raises AssertionError: When Color sensor saw nothing.

        """
        self.bv, self.bc, \
        self.br, self.bg, \
        self.bb = self.read_data()
        try:
            assert (self.br != 0 and self.bg != 0 and self.bb != 0)
        except AssertionError:
            raise AssertionError("Baselines colors are zero.")

    def get_percent_diff(self):
        """Calculates percent difference from baseline.
        
        :returns: percent differences of brightness, and colors.
        
        """
        diff_c = (self.color["clear"] - self.bc) / self.bc
        diff_r = (self.color["red"] - self.br) / self.br
        diff_g = (self.color["green"] - self.bg) / self.bg
        diff_b = (self.color["blue"] - self.bb) / self.bb
        return diff_c, diff_r, diff_g, diff_b

    def detects_color(self, color):
        """Checks to see if given color is present.
        
        :param color: Color to check for.
        :type color: string
        
        :returns: True if color found. False otherwise.

        """
        diff_c, diff_r, diff_g, diff_b = self.get_percent_diff()

        if color == "green":
            if (diff_g > diff_r) and (diff_g > diff_b):
                return True
        elif color == "red":
            if (diff_r > diff_g) and (diff_r > diff_b):
                return True
        elif color == "blue":
            if (diff_b > diff_g) and (diff_b > diff_r):
                return True
        else:
            return "Error: Unknown color"
            
        return False

    def watch_for_color(self, color, timeout=60):
        """Waits for given color to be found.
        
        :param color: Color to wait for.
        :type color: string
        :param timeout: Maximum time in seconds for which it will wait.
        :type timeout: float
        :returns: True when color is eventually found. False if never found.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if detects_color(color):
                return True
        return False

    def detects_color_diff_method(self, color, thresh=0.2):
        """Finds color based on the total % of total color that is seen. 
        
        Each percentage is a fraction of the total color (r+g+b)
        as seen by the color sensor. The percentages all add up 
        to 100.

        Note: This is experimental and not recommended for use.
        
        :param color: Color to search for.
        :type color: string
        :param thresh: Difference in percentage expected.
        :type thresh: float
        :returns: True if color is found. False otherwise.

        """
        # Reads in percentages of total color
        pv, pc, \
        percent_red,\
        percent_green, \
        percent_blue = self.get_percentage()

        total_color = self.color["red"] \
                    + self.color["green"] \
                    + self.color["blue"]

        total_base = self.br + self.bg + self.bb

        # Base percentages for each color
        percent_baser = self.br / total_base * 100
        percent_baseg = self.bg / total_base * 100
        percent_baseb = self.bb / total_base * 100

        # returns True when the percentage of a color goes up by thresh
        if color == "green":
            if percent_green - percent_baseg > thresh:
                return True
        elif color == "red":
            if percent_red - percent_baser > thresh:
                return True
        elif color == "blue":
            if percent_blue - percent_baseb > thresh:
                return True
        else:
            return "Error: Unknown color"
        return False


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
            # print "[{:8.3f}] ".format(elapsed)
            # print "v: {}, c: {:5.3f}, r: {:5.3f}, g: {:5.3f}, b: {:5.3f}".format(v, c, r, g, b)

            # if colorSensor.is_green():
                # print "Found green"
            if colorSensor.detects_color("green"):
                print "Found green, Percent method"

            # if colorSensor.is_green_diff_method():
                # print "diff method"

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
