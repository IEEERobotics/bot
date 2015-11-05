"""Encapsulates functionality of moving around robot arm"""

import simpy

import bot.lib.lib as lib
from bot.hardware.servo import Servo



class RobotArm(object):


   """An object that resembles a robotic arm with n joints"""
    def __init__(self, servo_assignments):

        for pwm in servo_assignments:

            self.joint_servos.append(Servo(pwm)) 
            
    
    @lib.api_call
    def set_joint_angle(self, joint, angle):
        """Sets the angle of an individual joint

        :param joint: Number of the joint (lowest joint being 1)
        :type joint: int
        :param angle: angle to be set (in degrees)
        :type angle: int
        """

        self.joint_servos[joint].position = angle 
