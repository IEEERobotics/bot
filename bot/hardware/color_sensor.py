"""Controls activity related to RGB color sensor."""

import time

from i2c_device.i2c_device import I2CDevice

import bbb.gpio as gpio_mod
import bbb.pwm as pwm_mod
import bot.lib.lib as lib


class ColorSensor(I2CDevice):

    """Wrapper class for TCS3472 I2C-based color sensor."""

    # TODO: Make these config items and load in __init__()
    max_c = 65536

    # Base values to be changed by get_baseline
    bv = 0.0
    bc = 0.0
    bg = 0.0
    br = 0.0
    bb = 0.0

    def __init__(self, testing):
        """Initialized I2C device, LED brightness PWM pin."""

        self.testing = testing
        # Handle off-bone runs
        if not self.testing:

            # Setup I2C
            I2CDevice.__init__(self, 1, 0x29, config='tcs3472_i2c.yaml')
            enable = self.registers['ENABLE']
            # id = self.registers['ID']
            # status = self.registers['STATUS']
            enable.write('PON', 'Enable')
            enable.write('AEN', 'Enable')
            enable = self.registers['ENABLE']  # TODO: Is this needed?


        else:
            # Fake device at address "0x00"
            I2CDevice.__init__(self, 1, 0x00, config='tcs3472_i2c.yaml')

        # Gets base values for comparisons to future readings.
        self.get_baseline()
        
        self.c = 0
        self.r = 0
        self.g = 0
        self.b = 0


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

    @lib.api_call
    def wait_for_ready(self, timeout=122):
        """Waits for ready switch to be activates before moving on.
        """
        t0 = time.time()
        print "value: ", self.ready_gpio.get_value()
        while time.time() - t0 > timeout:
            if self.ready_gpio.get_value():
                return True
        return False

    def read_data(self, bias_color="", bias_constant=0):
        """Reads in raw data directly from color_sensor.

        :param bias_color: One color can be made more sensitive.
            note: May cause false positives.
            recommended values are ~1%
        :param bias_constant: Percentage increase by which to bias.
        :returns: Validity, Clear (magnitude), Red, Green, Blue.

        """
        if not self.testing:
            valid = self.registers['STATUS'].read('AVALID')
            c = self.registers['CDATA'].read()
            r = self.registers['RDATA'].read()
            g = self.registers['GDATA'].read()
            b = self.registers['BDATA'].read()

            if bias_color == "green":
                g *= 1 + bias_constant / 100
            elif bias_color == "red":
                r *= 1 + bias_constant / 100
            elif bias_color == "blue":
                b *= 1 + bias_constant / 100

            self.c = c
            self.r = r
            self.g = g
            self.b = b

            return valid, c, r, g, b
        else:
            return 1, 1, 1, 1, 1

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

    def detect_on(self):
        """Detects if red light is on or off.

        """
        v, c, r, g, b = self.get_percentage()

        if r < 50.0:
            print "OFF"
        else:
            print "ON"

    def get_baseline(self, timeout=1):
        """Obtains "base" colors to work from.

        :raises AssertionError: When Color sensor saw nothing.

        """

        # Repeatedly attempts baseline if zeros are found.
        # Note: if this doesn't work on the first try, something
        # is usually wrong.
        start_time = time.time()
        attempt_count = 0
        while (time.time() - start_time) < timeout:
            self.bv, self.bc, \
                self.br, self.bg, \
                self.bb = self.read_data()
            attempt_count += 1
            if self.br != 0 and self.bg != 0 and self.bb != 0:
                break

    def get_percent_diff(self):
        """Calculates percent difference from baseline.

        :returns: percent differences of brightness, and colors.

        """
        self.read_data()
        diff_c = (self.c - self.bc) / self.bc
        diff_r = (self.r - self.br) / self.br
        diff_g = (self.g - self.bg) / self.bg
        diff_b = (self.b - self.bb) / self.bb

        # Green is weakest color, so bias in that direction.
        #diff_g *= 1.01

        return diff_c, diff_r, diff_g, diff_b

    @lib.api_call
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

    def decides_color(self):
        """Decides on color based on readings.

        :returns: Name of color found.
        """

        if self.detects_color("green"):
            return "green"
        elif self.detects_color("red"):
            return "red"
        elif self.detects_color("blue"):
            return "blue"

    @lib.api_call
    def watch_for_color(self, color, timeout=5):
        """Waits for given color to be found.

        :param color: Color to wait for.
        :type color: string
        :param timeout: Maximum time in seconds for which it will wait.
        :type timeout: float
        :returns: True when color is eventually found. False if never found.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.detects_color(color):
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
            percent_green, percent_blue = self.get_percentage()

        # total_color = self.color["red"] \
        #    + self.color["green"] \
        #    + self.color["blue"]

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
    cs = ColorSensor(False)

    # gets base values for all colors.
    time.sleep(0.5)
    cs.get_baseline()

    print "bv: {}, bc: {:5.3f},\
           br: {:5.3f}, bg: {:5.3f}, bb: {:5.3f}".format(
        cs.bv,
        cs.bc,
        cs.br,
        cs.bg,
        cs.bb)

    t0 = time.time()
    while True:
        try:
            #percentages = cs.get_percentage()
            data = cs.get_percent_diff()
            
            print "Red: {:5.3f}, Green: {:5.3f}, Blue: {:5.3f}".format(cs.r, cs.g, cs.b)
            print "Red: {:5.3f}, Green: {:5.3f}, Blue: {:5.3f}".format(data[1], data[2], data[3])
            
            print "color: ", max(data[1:4])
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    print "Done."

if __name__ == "__main__":
    read_loop()
