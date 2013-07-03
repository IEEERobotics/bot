#!/usr/bin/env python
# pass angle in degrees
# Wheel A = front left
# Wheel B = front Right
# Wheel C = Back Left
# Wheel D = Back Right
	
# Motion library to abstract wheel movement and macro moves from hardware.
from math import sin, cos, pi
from time import sleep

def iowrite(wheel, ds):
  print wheel, ds
	
def move(speed, angle, time=0):
  """Calculating voltage multiplier for each wheel, passing to io pins.

  :param speed: Magnitude of robot's translation speed.
  :type speed: float.
  :param angle: Angle at which robot should translate.
  :type angle: float.
  :param time: Time in seconds that robot should do this move.
  :type time: float.

  """

  # Calculate voltage multipliers
  front_left = speed * sin(angle*pi/180 + pi/4)
  front_right = speed * cos(angle*pi/180 + pi/4)
  back_left = speed * cos(angle*pi/180 + pi/4)
  back_right = speed * sin(angle*pi/180 + pi/4)  
  
  # Write to io pins.
  iowrite("front_left", front_left)
  iowrite("front_right", front_right)
  iowrite("back_left", back_left)
  iowrite("back_right", back_right)
  
  # Sleep for user defined amount of time
  sleep(time)
  
  # Stop robot movement.
  iowrite("front_left", 0)
  iowrite("front_right", 0)
  iowrite("back_left", 0)
  iowrite("back_right", 0)
  
def rotate(Rspeed, time=0):
  """Controlling rotation of robot"""
  
  #Calculate voltage multipliers
  front_left = Rspeed
  front_right = -Rspeed
  back_left = Rspeed
  back_right = -Rspeed
  
  # Write to io pins.
  iowrite("front_left", front_left)
  iowrite("front_right", front_right)
  iowrite("back_left", back_left)
  iowrite("back_right", back_right)
  
  # Sleep for user defined amount of time
  sleep(time)
  
  # Stop robot movement.
  iowrite("front_left", 0)
  iowrite("front_right", 0)
  iowrite("back_left", 0)
  iowrite("back_right", 0)
