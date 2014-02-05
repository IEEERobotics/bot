"""Logic for line follower."""

import sys
from time import time

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod
import lib.exceptions as ex
import follower
import pid as pid_mod

class LineFollower(follower.Follower):

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build IR arrays, logger and driver"""
        super(LineFollower, self).__init__()
        self.front_pid = pid_mod.PID()
        self.back_pid = pid_mod.PID()
        self.red_block = False
        self.blue_block = False
        self.intersection = False
        self.loss_line = False

    def get_red_block(self):
        return self.red_block

    def get_blue_block(self):
        return self.blue_block

    def get_intersection(self):
        return self.intersection

    def get_error_condition(self):
        return self.loss_line


    def follow(self, state_table):
        """Used to update the motors speed and angler motion."""
        self.state_table = state_table
        # Get the initial condition
        previous_time = time()
        # Init front_PId
        self.front_pid.set_k_values(1, 0, 0)
        # Inti back_PID
        self.back_pid.set_k_values(1, 0, 0)
        # Get current Heading
        self.heading = self.state_table.currentHeading
        # Continue until an error condition
        while True:
            # Assign the current states to the correct heading
            self.assign_states()
            # Check for error conditions        
            if self.error != 0:
                self.update_exit_state()
                return
            # Get the current time of the CPU
            current_time = time()
            # Call front PID
            self.sampling_time = current_time - previous_time
            # Call front PID
            front_error = self.front_pid.pid(
                0, self.front_state, self.sampling_time)
            # Call back PID
            back_error = self.back_pid.pid(
                0, self.back_state, self.sampling_time)
            # Update motors
            self.motors(front_error, back_error)
            # Take the current time set it equal to the previous time
            previous_time = current_time
        
    def update_exit_state(self):
        if(self.error == 1):
            self.intersection = True
        elif(self.error == 2):
            self.loss_line = True
        elif(self.error == 3):
            self.loss_line = True
        elif(self.error == 4):
            self.loss_line = True
        elif(self.error == 5):
            self.loss_line = True
        

    def motors(self, front_error, back_error):
        """Used to Update the motors speed and angler motion."""
        # Calculate translate_speed
        # MAX speed - error in the front sensor / total number
        # of states
        translate_speed =  100 - ( front_error / 16 )
        # Calculate rotate_speed
        # Max speed - Translate speed
        rotate_speed = 100 - translate_speed
        # Calculate translate_angle
        translate_angle = back_error * (180 / 16)
        if translate_angle < 0:
            # Swift to the left
            translate_angle = 360 - translate_angle
        else:
            # swift to the right
            translate_angle = translate_angle   
        if translate_speed > 100:
            # If translate_speed is greater than 100 set to 100
            translate_speed = 100
        elif translate_speed < 0:
            # If translate_speed is greater than 100 set to 100
            translate_speed = 0
        if rotate_speed > 100:
            # If rotate_speed is greater than 100 set to 100
            rotate_speed = 100
        elif rotate_speed < 0:
            # If rotate_speed is greater than 100 set to 100
            rotate_speed = 0
        # Adjust motor speeds 
        mec_driver_mod.compound_move(
            translate_speed, translate_angle, rotate_speed)

    def assign_states(self, current_ir_reading=None):
        """Take 4x16 bit arrays and assigns the array to proper orientations.

        Note that the proper orientations are front, back, left and right.

        """
        # Get the current IR readings
        if current_ir_reading is None:
            current_ir_reading = self.ir_hub.read_all()
        # Heading west
        if self.heading == 0:
            # Forward is on the left side
            self.front_state = self.get_position_lr(
                current_ir_reading["left"])
            # Back is on the right side
            self.back_state = self.get_position_rl(
                current_ir_reading["right"])
            # Left is on the back
            self.left_state = self.get_position_lr(
                current_ir_reading["back"])
            # Right is on the front
            self.right_state = self.get_position_rl(
                current_ir_reading["front"])
        # Heading east
        elif self.heading == 180:
            # Forward is on the right side
            self.front_state = self.get_position_lr(
                current_ir_reading["right"])
            # Back is on the left side
            self.back_state = self.get_position_rl(
                current_ir_reading["left"])
            # Left is on the front
            self.left_state = self.get_position_lr(
                current_ir_reading["front"])
            # Right is on the back
            self.right_state = self.get_position_rl(
                current_ir_reading["back"])
        # Heading south
        elif self.heading == 270:
            # Forward is on the front side
            self.front_state = self.get_position_lr(
                current_ir_reading["front"])
            # Back is on the back side
            self.back_state = self.get_position_rl(
                current_ir_reading["back"])
            # Left is on the left
            self.left_state = self.get_position_lr(
                current_ir_reading["left"])
            # right is on the right
            self.right_state = self.get_position_rl(
                current_ir_reading["right"])
            # Heading north
        elif self.heading == 90:
            # Forward is on the right side
            self.front_state = self.get_position_lr(
                current_ir_reading["back"])
            # Back is on the left side
            self.back_state = self.get_position_rl(
                current_ir_reading["front"])
            # Left is on the front
            self.left_state = self.get_position_lr(
                current_ir_reading["right"])
            # Right is on the back
            self.right_state = self.get_position_rl(
                current_ir_reading["left"])
        if((self.front_state > 15) or (self.back_state > 15) or
            (self.right_state < 16) or (self.left_state < 16)):
            if((self.right_state < 16) or (self.left_state < 16) or 
                (self.front_state == 17) or (self.back_state == 17)):
                # Found Intersection
                self.error = 1
            elif((self.back_state == 18) or (self.front_state == 18)):
                # at high angle
                self.error = 5
            elif((self.front_state == 16) and (self.back_state == 16)):
                # Front and back lost line
                self.error = 2
            elif(self.front_state == 16):
                # Front lost line
                self.error = 3
            elif(self.back_state == 16):
                # Back lost line
                self.error = 4
        else:
            self.error = 0
                


    def get_position_lr(self, readings):
        """Reading the IR sensors from left to right
        
        Calculates the current state in reference to center from 
        left to right. States go form -15 to 15.

        """
        self.hit_position = []
        state = 0.0
        for index, value in enumerate(readings):
            if(value == 1):
               self.hit_position.append(index)
        if len(self.hit_position) > 3:
            # Error: Intersection detected
            return 17
        if len(self.hit_position) == 0:
            # Error: No line detected
            return 16
        if len(self.hit_position) == 3:
            # Error: Bot at large error
            return 18
        state = self.hit_position[0] * 2
        if len(self.hit_position) > 1:
            if self.hit_position[1] > 0:
                state = state + 1
            if abs(self.hit_position[0] - self.hit_position[1]) > 1:
                # Error: Discontinuity in sensors
                return 19
        state = state - 15
        return state

    def get_position_rl(self, readings):
        """Reading the IR sensors from left to right   
        
        Calculates the current state in reference to center from 
        left to right. States go form -15 to 15.

        """
        self.hit_position = []
        state = 0.0
        for index, value in enumerate(readings):
            if(value == 1):
               self.hit_position.append(index)
        if len(self.hit_position) > 3:
            # Error: Intersection detected
            return 17
        if len(self.hit_position) == 0:
            # Error: No line detected
            return 16
        if len(self.hit_position) == 3:
            # Error: Bot at large error
            return 18
        state = self.hit_position[0] * 2
        if len(self.hit_position) > 1:
            if(self.hit_position[1] > 0):
                state = state + 1
            if(abs(self.hit_position[0] - self.hit_position[1]) > 1):
                # Error: Discontinuity in sensors
                return 19
        state = (state - 15) * -1
        return state
