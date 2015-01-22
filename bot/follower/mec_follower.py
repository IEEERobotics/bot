"""Logic for following lines using Mecanum wheels."""

import sys
from time import time, sleep

import numpy as np

import bot.lib.lib as lib
import bot.hardware.ir_hub as ir_hub_mod
import bot.driver.mec_driver as mec_driver_mod
import pid as pid_mod

class MecFollower(object):
    """Subclass of Follower for line-following using mecanum wheels."""
    
    def __init__(self):
        # Building logging
        self.logger = lib.get_logger()
        
        # Build subsystems 
        self.ir_hub = ir_hub_mod.IRHub()
        self.ir_hub.thresh = 100
        self.driver = mec_driver_mod.MecDriver()
        #self.color_sensor = color_sensor_mod.ColorSensor()
        
        # Build PID class
        self.front_right = pid_mod.PID()
        self.front_right.error = 0.0
        self.front_left = pid_mod.PID()
        self.front_left.error = 0.0
        self.back_right = pid_mod.PID()
        self.back_right.error = 0.0
        self.back_left = pid_mod.PID()
        self.back_left.error = 0.0
        
        self.rotate = pid_mod.PID()
        self.rotate_error = 0.0
        
        self.translate_speed=75
    
    @lib.api_call
    def update(self):
    # get IR readingsmec_driver_mod
        self.ir_readings = self.ir_hub.read_all_loop
        self.ir_f = self.ir_readings["front"]
        self.ir_b = self.ir_readings["back"]
        self.ir_l = self.ir_readings["left"]
        self.ir_r = self.ir_readings["right"]
        
        self.v_front_left = self.driver.get_motor("front_left")
        self.v_front_right = self.driver.get_motor("front_right")
        self.v_back_left = self.driver.get_motor("back_left")
        self.v_back_right = self.driver.get_motor("back_right") 
        
        i = 0
        while i<=7:
            if (self.ir_f[i] <= 200):
                self.ir_front[i] = 1
            else:
                self.ir_front[i] = 0

            if (self.ir_b[i] <= 200):
                self.ir_back[i] = 1
            else:
                self.ir_back[i] = 0
            
            if (self.ir_l[i] <= 200 ):
                self.ir_left[i] = 1
            else:
                self.ir_left[i] = 0

            if (self.ir_r[i] <= 200):
                self.ir_right[i] = 1
            else: 
                self.ir_right[i] = 0
    
            i = i+1

        return "ir_front: {}, v_back_left: {}, v_back_right: {}".format(self.ir_front, self.v_back_left, self.v_back_right)

    @lib.api_call
    def get_translate_speed(self):
        return self.translate_speed
    
    @lib.api_call
    def forward(self):
        sum_front = (ir_front[0]+ir_front[1]+ir_front[2]+ir_front[3]+ir_front[4]+ir_front[5]+ir_front[6]+ir_front[7])
        print sum_front
        if(sum_front == 2):
            front_error = (ir_front[0]*(-3.5)+ir_front[1]*(-2.5)+ir_front[2]*(-1.5)+ir_front[3]*(-0.5)+ir_front[4]*(0.5)+ir_front[5]*(1.5)+ir_front[6]*(2.5)+ir_front[7]*(3.5))-0
            current_time = time()
            self.sampling_time = current_time - previous_time
            self.front_right.set_k_values(1,0,0)
            self.front_error = self.front.pid(0,front_error,self.sampling_time)
            previous_time = current_time
            v_back_left_speed = v_back_left+self.front_error
            v_back_right_speed = v_back_back-self.front_error
            self.driver.set_motor("front_left",v_back_left_speed)
            self.driver.set_motor("back_left", v_back_back_speed)
        
