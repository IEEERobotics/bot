"""The 2015 competition involved playing a Simon Says Caribiner toy.
This device uses an actuater made up of a stepper motor and a servo.
The servo is used for actuating two plastic bits towards the toy, and
the stepper motor is used for controlling that actuators position.
"""

import bot.lib.lib as lib
import bbb as bbb_mod
from bot.hardware.SimonSaysHardware import SimonSaysHardware
from bot.hardware.pot import Pot

from time import sleep

class SimonPlayer(object):

    def __init__(self):
        """Initializes the simon says player.

        :param simon_config: config entry mapping simons inputs
        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.color_gpio = self.config["simon"]["colors"]

        self.color_detectors = dict()
        for color in self.color_gpio:
            self.color_detectors[color] = \
                bbb_mod.GPIO(self.color_gpio[color])

        self.pot = Pot("pot1", self.color_detectors)

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
                print self.read_all()
                sleep(0.1)
            except KeyboardInterrupt:
                break

    def read_input(self):
        """ This function returns the color (encoded to the sensor)
        that is turns on.
        """
        while True:
            try:
                for d in self.color_detectors:
                    if(self.color_detectors[d].get_value() != 0):
                        return d
            except KeyboardInterrupt:
                break

    @lib.api_call
    def test_turn(self, pos):
        """Test whether the stepper turns and presses button at the 
        specified position.
        
        """
        self.simon.turn(pos)

    @lib.api_call
    def test_press_start(self):
        """Test whether the servo presses the start button."""
        self.simon.press_start()

    @lib.api_call
    def play_simon(self):
        """ Test function for playing the actual game once the 
        Simon is gripped.
        """
        round_no = 1
        colors = {"yellow" : 1, "blue" : 2, "red" : 3, "green" : 4}
        # 1) Press the start button
        self.simon.press_start()
        self.pot.find_ambient_light()
 
        while True:
            try:
                
                # 2) Read the input GPIOs until one of the value changes
                # and pass the input into the algorithm to get the 
                # positions to press the buttons

                pos = dict()
                for i in range(0,round_no):
                    sensor_reading = self.read_input()
                    # DEBUG
                    print sensor_reading
                    actual_position = (colors[sensor_reading] \
                        + self.simon.position -1) % 4
                    if(actual_position == 0):
                        actual_position = 4
                    pos[i] = actual_position

                # 4) Call the self.turn() method with the position numbers
                # the specified number of times
                for i in range(0, round_no):
                    self.simon.turn(pos[i])
                # 5) Increment round_no
                round_no = round_no + 1

                if(round_no > 5):
                    break
            except KeyboardInterrupt:
                break
        # reset to position 1 before exiting
        self.simon.turn(1)
        # SIDE-EFFECT: Actuator is going to reset to position 1
        # and press the button before exiting
