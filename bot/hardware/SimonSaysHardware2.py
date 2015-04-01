"""Encapsulates functionality required to operate the Simon Says Servo hardware - v.2"""

import time
from math import pi

import bot.lib.lib as lib
from bot.hardware.micromotor import Micromotor
from bot.hardware.lightDetector import LightDetector

class SimonSaysHardware2(object):

    """Simon Says manipulator that encapsulates 5 micromotors and ADC/photoresistor input"""

    def __init__(self):
        
        # Load and store logger
        self.logger = lib.get_logger()

        # Load and store configuration dict
        self.config = lib.get_config()

        if self.config["test_mode"]["simon_player"]:
            # yet to add trivial code
            pass

        else:
            # Build the 5 micromotors
            self.motor1 = Micromotor(self.config["simon"]["motor1"])
            self.motor2 = Micromotor(self.config["simon"]["motor2"])
            self.motor3 = Micromotor(self.config["simon"]["motor3"])
            self.motor4 = Micromotor(self.config["simon"]["motor4"])
            self.motor5 = Micromotor(self.config["simon"]["motor5"])

            # TODO (Vijay) : Build the input detectors
            self.input_detector = LightDetector()
           

    # TODO (Vijay) : press_* yet to be tested.
    @lib.api_call
    def press_start(self):
        self.motor1.forward()
        self.timer.sleep(1)
        self.motor1.stop()
        self.motor1.backward()
        self.timer.sleep(1)
        self.motor1.stop()

    @lib.api_call
    def press_red(self):
        self.motor2.forward()
        self.timer.sleep(1)
        self.motor2.stop()
        self.motor2.backward()
        self.timer.sleep(1)
        self.motor2.stop()

 
    @lib.api_call
    def press_blue(self):
        self.motor3.forward()
        self.timer.sleep(1)
        self.motor3.stop()
        self.motor3.backward()
        self.timer.sleep(1)
        self.motor3.stop()

 
    @lib.api_call
    def press_green(self):
        self.motor4.forward()
        self.timer.sleep(1)
        self.motor4.stop()
        self.motor4.backward()
        self.timer.sleep(1)
        self.motor4.stop()

 
    @lib.api_call
    def press_yellow(self):
        self.motor5.forward()
        self.timer.sleep(1)
        self.motor5.stop()
        self.motor5.backward()
        self.timer.sleep(1)
        self.motor5.stop()
