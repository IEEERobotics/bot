"""Logic for line following."""

import sys

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod
import lib.exceptions as ex
from time import time


class PIDFollower(object):

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build Ir arrays, logger and drivers."""
        self.logger = lib.get_logger()
        self.irs = ir_hub_mod.IRHub()
        self.driver = mec_driver_mod.MecDriver()
        self.front_reading = 0
        self.back_reading = 0
        self.left_reading = 0
        self.right_reading = 0
        self.front_position = [0, 0, 0, 0]
        self.back_position = [0, 0, 0, 0]
        self.left_position = [0, 0, 0, 0]
        self.right_position = [0, 0, 0, 0]
        self.current_heading = 0
        self.front_kp = 1
        self.front_kd = 1
        self.front_ki = 1
        self.back_ke = 1
        self.back_kd = 1
        self.back_ki = 1
        self.heading = 2.8125
        self.previous_front_i_error = 0
        self.previous_back_i_error = 0

    def follow(self, state_table):
        """Accept and handle fire commands."""
        self.state_table = state_table
        # Get the intial condetion
        previous_time = time()
        #while(1)
        # Assign the arrays to the correct heading
        self.assign_arrays()
        # Get the current time of the cpu
        if((self.front_reading < 0)or(self.back_reading < 0)):
            print "Found X"
        current_time = time()
        # Calculate the position of the forward and back sensers
        self.calculate_position()
        # Call front PID
        self.sampling_time = current_time - previous_time
        # Call front PID
        front_error = self.front_pid()
        # Call back PID
        back_error = self.back_pid()
        # Update motors
        self.motors(front_error, back_error)
        # Take the current time set it equal to the privious time
        previous_time = current_time

    def motors(self, front_error, back_error):
        """Used to update the motors speed and angler moation."""
        pass

    def front_pid(self):
        """Calculate the k value for the forward pid."""
        # Calculate the papration error
        p_error = (self.heading - self.front_position[0])
        # Calculate the derivation error
        d_error = (self.front_position[0] - \
                   self.front_position[1]) / self.sampling_time
        # Calulate the intergration error
        i_error = (self.front_position[0] + \
                   self.front_position[1]) / 2 * self.sampling_time + \
                   self.previous_front_i_error
        # Update the previous intergration error to the new error
        self.previous_front_i_error = i_error
        # Return the total error for the front of the bot
        return self.front_kp * p_error + self.front_kd * d_error + \
                                       self.front_ki * i_error

    def back_pid(self):
        """Calculate the k value for the back PID."""
        # Caculate the papration error
        p_error = (self.heading - self.back_position[0])
        # Calculate the derivation error
        d_error = (self.back_position[0] - self.back_position[1]) / \
                   self.sampling_time
        # Calculate the intergration error
        i_error = (self.back_position[0] + self.back_position[1]) / \
                   2 * self.sampling_time + self.previous_back_i_error
        # Update the previous intergration error with the new error
        self.previous_back_i_error = i_error
        # Return the total error fot the back of the bot
        return self.front_kp * p_error + self.front_kd * d_error + \
                                       self.front_ki * i_error

    def calculate_position(self):
        """Calculate the position of the line as it is on the bot."""
        # Get rid of the last entry
        self.front_position = self.front_position[:len(self.front_position) - \
                                                   1]
        # Add current reading to the list
        self.front_position.insert(0, self.front_reading)
        # Get rid of the last entry
        self.front_position = self.front_position[:len(self.front_position) - \
                                                   1]
        # Add current reading to the list
        self.front_position.insert(0, self.back_reading)

    def assign_arrays(self):
        """Take 4x16 bit arrays and assigns the array to proper orientations.

        Note that the 'proper orientaitons are front, back, left and right.

        """
        self.heading = self.state_table.currentHeading
        current_ir_reading = self.irs.read_all_arrays()
        # Heading west
        if self.heading == 0:
            # Forward is on the left side
            self.front_reading = self.get_position_lr(
                                        current_ir_reading["left"])
            # Back is on the right side
            self.back_reading = self.get_position_rl(
                                        current_ir_reading["right"])
            # Left is on the back
            self.left_reading = self.get_position_lr(
                                        current_ir_reading["back"])
            # Right is on the fornt
            self.right_reading = self.get_position_rl(
                                        current_ir_reading["front"])
        # Heading east
        elif self.heading == 180:
            # Forward is on the right side
            self.front_reading = self.get_position_lr(
                                        current_ir_reading["right"])
            # Back is on the left side
            self.back_reading = self.get_position_rl(
                                        current_ir_reading["left"])
            # Left is on the front
            self.left_reading = self.get_position_lr(
                                        current_ir_reading["front"])
            # Right is on the back
            self.right_reading = self.get_position_rl(
                                        current_ir_reading["back"])
        # Heading south
        elif self.heading == 270:
            # Forward is on the front side
            self.front_reading = self.get_position_lr(
                                        current_ir_reading["front"])
            # Back is on the back side
            self.back_reading = self.get_position_rl(
                                        current_ir_reading["back"])
            # Left is on the left
            self.left_reading = self.get_position_lr(
                                        current_ir_reading["left"])
            # right is on the right
            self.right_reading = self.get_position_rl(
                                        current_ir_reading["right"])
            # Heading nouth
        elif self.heading == 90:
            # Forward is on the right side
            self.front_reading = self.get_position_lr(
                                        current_ir_reading["back"])
            # Back is on the left side
            self.back_reading = self.get_position_rl(
                                        current_ir_reading["front"])
            # Left is on the front
            self.left_reading = self.get_position_lr(
                                        current_ir_reading["right"])
            # Right is on the back
            self.right_reading = self.get_position_rl(
                                        current_ir_reading["left"])

    def get_position_lr(self, array):
        """Returns a position in bits from left to right."""
        # Set initial position
        position = 0
        # Set initial sener hits
        position_count = 0
        # Move through the list and look for hits
        for n, v in enumerate(array):
            # Count the if there is a hit
            if(v == 1):
                # Count the number of hits
                position_count = position_count + 1
                # Add the position to the last position
                position = position + v * (15. - n) * 5.625 / 15
        # If there ate more than 4 hits than stop line following
        if(position_count > 3):
            # Return error condition
            return -1
        # If there is only one hit
        elif(position_count == 1):
            # Return the position
            return position
        # If there are no hits
        elif(position_count == 0):
            return 0
        # If there at more than one and less than 3 hits find the avarge
        else:
            # As long as hits are side by side
            if(self.side_by_side(array) == 1):
                # Return the avarge
                return position / position_count
            else:
                return -2

    def side_by_side(self, array):
        """Determines if array hits are beside one another."""
        # The index of the frist hit
        first_hit = array.index(1)
        # The max of the 2 (or one negbhors )
        if(first_hit != 0 or first_hit != len(array)):
            # Max neigbor equals the max value of either neighbor
            max_neighbor = max(array.index(first_hit + 1),
                               array.index(frist_hit - 1))
        elif(first_hit == 0):
            max_neighbor = array.index(first_hit + 1)
        else:
            max_neighbor = array.index(first_hit - 1)
        # If the max neighbor does not equal 1
        if(max_neighbor != 1):
            # Return -1 (fail case)
            return -1
        else:
            # Return 1 (pass case)
            return 1

    def get_position_rl(self, array):
        """Returns a position in bits from right to left."""
        # Set initial position
        position = 0
        # Set initial hit count to 0
        position_count = 0
        # Move through the list and look for hits
        for n, v in enumerate(array):
            # If there is a hit
            if(v == 1):
                # Count the number of hits
                position_count = position_count + 1
                # Add the position to the position
                position = position + v * (n + 0.0) * 12 / 15
        # If there are more than 4 hits
        if(position_count > 3):
            # Return error condition
            return -1
        # If there is one condition
        elif(position_count == 1):
            # Return the position
            return position
        elif(position_count == 0):
            return 0
        # If there are less than 4 hits and more than one hit
        else:
            # As long as hits are side by side
            if(self.side_by_side(array) == 1):
                # Return the avarge
                return position / position_count
            else:
                return -2
