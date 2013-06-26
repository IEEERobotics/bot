#!/usr/bin/env python
# pass angle in degrees
# Wheel A = front left
# Wheel B = front Right
# Wheel C = Back Left
# Wheel D = Back Right
	
# Motion library to abstract wheel movement and macro moves from hardware.
from math import sin, cos, pi

def iowrite(wheel, ds):
  print wheel, ds
	
def move(speed, angle)
  """Calculating voltage multiplier for each wheel, passing to io pins."""

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