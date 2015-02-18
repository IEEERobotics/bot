"""The 2015 competition involved playing a Simon Says Caribiner toy.
This device uses an actuater made up of a stepper motor and a servo.
The servo is used for actuating two plastic bits towards the toy, and
the stepper motor is used for controlling that actuators position.
"""

import bot.lib.lib as lib
import bbb as bbb_mod
from bot.hardware import SimonSaysHardware

from time import sleep

class SimonPlayer(object):

    def __init__(self):
        """Initializes the simon says player.

        :param simon_config: config entry mapping simons inputs
        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.is_testing = self.config["test_mode"]["simon_player"]
        
        self.color_gpio = self.config["simon"]["colors"]

        self.color_detectors = dict()
        for color in self.color_gpio:
            self.color_detectors[color] = \
                bbb_mod.GPIO(self.color_gpio[color])

        # init all detectors as inputs
        for d in self.color_detectors:
            self.color_detectors[d].input()

        # construct the stepper motor hardware
        self.simon = SimonSaysHardware()

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
    def read_all_loop(self):

        while True:
            try:
                self.read_all()
                sleep(0.1)
            except KeyboardInterrupt:
                break
