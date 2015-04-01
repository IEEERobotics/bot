"""Light detectors built using ADCs and photoresistors.
"""

import bot.lib.lib as lib
import bot.hardware.pot import Pot

class LightDetector(object):

    def __init(self):
        """Sets up the light detecting hardware.

        """

        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.color_gpio = self.config["simon"]["colors"]

        self.color_detectors = dict()
        for color in self.color_gpio:
            self.color_detectors[color] = \
                bbb.mod.GPIO(self.color_gpio[color])

        self.pot = Pot("pot1", self.color_detectors)

        # init all the detectors as inputs
        for d in self.color_detectors:
            self.color_detectors[d].input()

    @lib.api_call
    def read_all(self):
        """read current value from all four detectors.

        :return: dict {"red":<val>, "green":<val>,
                        "blue":<val>, "yellow":<val>}
        """
        readings = dict()
        for d in self.color_detectors:
            readings[d] = self.color_detectors[d].get_value()
        return readings

    @lib.api_call
    def read_input(self):
        """ This function returns the color (encoded to the sensor)
        that is turned on.
        """
        while True:
            try:
                for d in self.color_detectors:
                    if(self.color_detectos[d].get_value() != 0)
                        return d
            except KeyboardInterrupt:
                break
