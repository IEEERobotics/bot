#!/usr/bin/env python
"""Pass low-level move commands to motors with mecanum wheels."""

from math import sin, cos, pi, floor

import driver
import lib.lib as lib


class MechDriver(driver.Driver):

    """Subclass of Driver for movement with mecanum wheels.

    TODO(dfarrell07): Override Driver.move with translate + rotate combo code.

    Motor A = front left
    Motor B = front Right
    Motor C = Back Left
    Motor D = Back Right

    """

    def __init__(self):
        """Run superclass's init."""
        super(MechDriver, self).__init__()
    	max_speed = 10

    def iowrite(self, motor, ds):
        """Write to IO pens that control the motors.

        TODO(dfarrell07): This is a stub

        :param motor: Motor to set speed of.
        :type ds: string
        :param ds: Duty cycle that motor should be set to.
        :type ds: float

        """
        self.logger.debug("IO write: motor: {}, ds: {}".format(motor, ds))
		

    def basic_move(self, speed, angle, rotate_speed):
        """Build low-level commands for holonomic translations with rotations.

        :param speed: Magnitude of robot's translation speed.
        :type speed: float
        :param angle: Angle in degrees at which robot should translate.
        :type angle: float
        :param rotate_speed: Desired rotational speed.
        :type rotate_speed: float

        """
        self.logger.debug("Speed: {}, angle {}, rotate speed {}".format(speed,
                                                            angle,
                                                            rotate_speed))

<<<<<<< HEAD
        # Calculate speed ratios
        front_left = speed * sin(angle*pi/180 + pi/4) + rotate_speed
        front_right = speed * cos(angle*pi/ 180 + pi/4) - rotate_speed
        back_left = speed * cos(angle*pi/ 180 + pi/4) + rotate_speed
        back_right = speed * sin(angle*pi/180 + pi/4) - rotate_speed
		
		#Calculate duty cycle (ratio to max_speed)
		#Todo for Ahmed: Run tests to find out what max_speed should be, if it should just be 'speed'.
		front_left_ds = floor(front_left / max_speed * 100)
		front_right_ds = floor(front_right / max_speed * 100)
		back_left_ds = floor(back_left / max_speed * 100)
		back_right_ds = floor(back_right / max_speed * 100) 
		
		#Prevent invalid duty cycle values.
		if front_left_ds > 100:
		  front_left_ds = 100
		if front_right_ds >100:
		  front_right_ds = 100
		if back_left_ds > 100:
		  back_left_ds = 100
		if back_right_ds > 100:
		  back_right_ds = 100
		  
		if front_left_ds < 0:
		  front_left_ds = 0
		if front_right_ds <0:
		  front_right_ds = 0
		if back_left_ds < 0:
		  back_left_ds = 0
		if back_right_ds < 0:
		  back_right_ds = 0
		 
		
		#Determine direction of wheel.
		#Bool will determine value of direction pin.
		if front_left > 0:
		  front_left_forward = True
		if front_right > 0:
		  front_right_forward = True
		if back_left > 0:
		  back_left_forward = True
		if back_right > 0:
		  back_right_foward = True
  
        # Write to IO pins.
        self.iowrite("front_left", front_left_ds)
        self.iowrite("front_right", front_right_ds)
        self.iowrite("back_left", back_left_ds)
        self.iowrite("back_right", back_right_ds)
