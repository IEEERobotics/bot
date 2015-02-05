"""The 2015 competition involved playing a Simon Says Caribiner toy.
This device uses an actuater made up of a stepper motor and a servo.
The servo is used for actuating two plastic bits towards the toy, and
the stepper motor is used for controlling that actuators position.
"""

import bot.lib.lib as lib
import bbb as bbb_mod


class SimonPlayer(object):

    def __init__(self, simon_config):
        """Initializes the simon says player.

        :param simon_config: config entry mapping simons inputs
        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.is_testing = self.config["test_mode"]["simon_player"]

        self.red_detector = bbb_mod.GPIO(self.config["simon"]["red"]
        self.green_detector = bbb_mod.GPIO(self.config["simon"]["green"]
        self.blue_detector = bbb_mod.GPIO(self.config["simon"]["blue"]
        self.yellow_detector = bbb_mod.GPIO(self.config["simon"]["blue"]

