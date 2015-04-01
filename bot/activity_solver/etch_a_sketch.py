"""etch_a_sketch from Arduino"""

import sys
from time import time
from time import sleep
import numpy as np

import bot.lib.lib as lib
from bot.hardware.stepper_motor import Stepper_motor

class etch_a_sketch(object):
    
    """Class for abstracting stepper motor settings."""

    def __init__(self):
        
        self.logger = lib.get_logger()
        self.config = lib.get_config()
        
        if self.config["test_mode"]["etch_a_sketch"]:
            # add code for test mode
            pass

        else:
            self.vert_motor = Stepper_motor(self.config["etch_a_sketch_motors"]["left_stepper"])
            self.horiz_motor = Stepper_motor(self.config["etch_a_sketch_motors"]["right_stepper"])
            self.vert_motor.speed = 80
            self.horiz_motor.speed = 80

        if (self.vert_motor.speed==80) && (self.horiz_motor.speed ==80):
            print "Speed Assigned"

    @lib.api_call
    def verify(self):
        print "Object built"

    @lib.api_call
    def drawI(self):
        x = 0
        while (x<6):
            self.vert_motor.clockwise()
            x+=1
        sleep(1)

    @lib.api_call
    def drawE(self):
        for x in xrange(1,13):
            self.horiz_motor.counter_clockwise()
        for x in xrange(1,7):
            self.horiz_motor.clockwise()
        for x in xrange(1,2):
            self.vert_motor.clockwise()
        for x in xrange(1,7):
            self.horiz_motor.counter_clockwise()
        for x in xrange(1,7):
            self.horiz_motor.clockwise()
        for x in xrange(1,2):
            self.vert_motor.clockwise()
        sleep(1)
        

    
    @lib.api_call
    def draw(self):
        for x in xrange(1,100):
            self.drawI()
            self.drawE()
            self.drawE()
            self.drawE()

        
        
        


