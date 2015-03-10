"""etch_a_sketch from Arduino"""

import sys
from time import time
from time import sleep
import numpy as np

import bot.lib.lib as lib
import bot.hardware.stepper_motor.py

class etch_a_sketch(object):
    
    """Class for abstracting stepper motor settings."""

    def _init_(self):
        
        self.logger = lib.get_logger()
        self.config = lib.get_config()
        
        if self.config["test_mode"]["etch_a_sketch"]:
            # add code for test mode
            pass

        else:
            self.vert_motor = Stepper_motor(self.config["etch_a_sketch_motors"]["left_stepper"])
            self.horiz_motor = Stepper_motor(self.config["etch_a_sketch_motors"]["right_stepper"])
            self.vert_motor.speed = self.hardware.Stepper_motor.speed(60)
            self.horiz_motor.speed = self.hardware.Stepper_motor.speed(60)


    def drawI(self):
        x = 0
        while (x<6):
            self.vert_motor.clockwise
            x+=1
        time.sleep(1)


    def drawE(self):
        for x in xrange(1,13):
            self.horiz_motor.counter_clockwise
        for x in xrange(1,7):
            self.horiz_motor.clockwise
        for x in xrange(1,2):
            self.vert_motor.clockwise
        for x in xrange(1,7):
            self.horiz_motor.counter_clockwise
        for x in xrange(1,7):
            self.horiz_motor.clockwise
        for x in xrange(1,2):
            self.vert_motor.clockwise
        time.sleep(1)
        

    
    @lib.api_call
    def draw(self):
        while true:
            self.drawI()
            self.drawE()
            self.drawE()
            self.drawE()

        
        
        


