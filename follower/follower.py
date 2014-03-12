"""Logic for line following."""

import sys
from time import time
from time import sleep
import numpy as np

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod
import pid as pid_mod


class Follower(object):

    """Follows a line, detects intersections and stop conditions."""

    #Class variables
    #Array_Conditions
    Large_Object = 17  #the array sees a large object
    No_Line = 16 #the array see no line
    Noise = 19 #white values not next to each other
    
    #Variables for read_binary calls
    White_Black = False  #True= white line, False= black line

    def __init__(self):
        # Build logger
        self.logger = lib.get_logger()

        # Build subsystems
        self.ir_hub = ir_hub_mod.IRHub()
        self.ir_hub.thrsh = 100
        self.driver = mec_driver_mod.MecDriver()

        # Build PIDs
        self.strafe = pid_mod.PID()
        self.front_error = 0.0
        self.rotate_pid = pid_mod.PID()
        self.rotate_error= 0.0
        self.error = "NONE"
        
        # motor variables
        self.translate_speed =  60

        #state variables
        self.front_state = Follower.No_Line
        self.back_state = Follower.No_Line
        self.left_state = Follower.No_Line
        self.right_state = Follower.No_Line

        # post error vars
        self.intersection = False
        self.lost_line = False
        self.timeLastUpdated = -1.0
        self.on_x = False

    @lib.api_call
    def get_translate_speed(self):
        return self.translate_speed

    @lib.api_call
    def set_translate_speed(self,speed):
        self.translate_speed = speed

    @lib.api_call
    def update(self):
        """Read IR values, compute aggregates."""
        ir_readings = self.ir_hub.read_binary(False)
        for name, reading in ir_readings.iteritems():
            reading_arr = np.int_(reading)  # convert readings to numpy array
            reading_sum = np.sum(np_reading)  # = no. of units lit
            if reading_sum > 0:
                self.ir_agg[name] = (np.sum(self.ir_pos * reading_arr)
                                    / reading_sum)
            else:
                self.ir_agg[name] = None
        self.timeLastUpdated = time.time()
   
    @lib.api_call
    def get_strafe_error(self):
        return self.strafe_error

    @lib.api_call
    def get_rotate_error(self):
        return self.rotate_error

    @lib.api_call
    def is_start(self):
        return True  # TODO: Use color sensor

    @lib.api_call
    def is_on_line(self):
        return (not self.lost_line)  # TODO: Use IR sensors to perform check

    @lib.api_call
    def is_on_x(self):
        return self.intersection  # TODO: Use IR sensors to perform check

    @lib.api_call
    def is_on_blue(self):
        return True  # TODO: Use color sensor

    @lib.api_call
    def is_on_red(self):
        return True  # TODO: Use color sensor
 
    @lib.api_call
    def follow(self, heading, on_x=False):
        """Follow line along given heading"""
        self.on_x = on_x
        # Get the initial conditioni
        self.heading = heading
        previous_time = time()
        # Init front_PID
        self.strafe.set_k_values(8, 0, .1)
        # Inti rotate_PID
        self.rotate_pid.set_k_values(6, 0, 0)
        # Get current heading
        self.heading = heading
        # Continue until an error condition
        count_object=0 

        while True:
            # Assign the current states to the correct heading
            self.assign_states()
            # Check for error conditions
            if self.error != "NONE":
                #require two succesive large_object readings to exit
                if self.error=="LARGE_OBJECT" and count_object<1:
                    count_object += 1
                    continue
                self.update_exit_state()
                self.logger.info("Error: {}".format( self.error ))
                self.logger.info("FS: {}, BS: {}, lS: {}, RS: {}".format( 
                    self.front_state,
                    self.back_state,
                    self.left_state,
                    self.right_state))
                self.driver.move(0,0)
                return self.error
            
            # average states.
            bot_position = (self.front_state + self.back_state)/2
            # Get the current time of the CPU
            current_time = time()
            self.sampling_time = current_time - previous_time
            # Call PID
            self.strafe_error = self.strafe.pid(
                0, bot_position, self.sampling_time)
            #calculate difference between array's for approx. pseudo angle 
            bot_angle = (self.front_state - self.back_state)
            # Call Rotate PID
            self.rotate_error = self.rotate_pid.pid(
                0, bot_angle, self.sampling_time)
            # Report errors from strafe and rotate pid's 
            self.logger.info("FS: {}, BS {}, LS {}, RS {}, StrafeErr: {}, RotErr: {}".format(
                self.front_state,
                self.back_state,
                self.left_state,
                self.right_state,
                self.strafe_error,
                self.rotate_error))
            # Update motors
            self.motors(bot_angle)
            # Take the current time set it equal to the previous time
            previous_time = current_time


    @lib.api_call
    def rotate_on_x(self,direction="left",speed=100,time=0.7):
        #After center_on_x, rotate in the commanded directions
        #by 90 degrees. 
        if(direction=="left"):
            sign = 1
        elif(direction=="right"):
            sign = -1
        else:
            self.logger.error("Bad param direction, please use left or right")
            return "DONE"

        # sign turns in correct direction
        self.driver.rotate(sign*speed) 

        sleep(time)

        self.driver.move(0,0)

        return "Done"

    @lib.api_call
    def report_states(self):
        # for debug of IR sensor state
        current_ir_reading = self.ir_hub.read_binary(Follower.White_Black)
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
        self.logger.info("front = {}".format(self.front_state))
        self.logger.info("back = {}".format(self.back_state))
        self.logger.info("left = {}".format(self.left_state))
        self.logger.info("right = {}".format(self.right_state))
    
    @lib.api_call
    def oscillate(self, heading, osc_time=1):
        """Oscillate sideways, increasing in amplitude until line is found"""

        # Time in seconds for which bot oscillates in each direction.
        # Speed at which the bot is oscillating.
        # Increase in speed after each oscillation cycle.
        # Todo(Ahmed): Find reasonable constants.
        osc_speed = 10
        osc_increment = 10

        # The oscillation directions, perpendicular to parameter "heading"
        angle1 = heading + 90
        angle2 = heading - 90
        self.logger.debug(
            "Pre-correction angles: angle1: {}, angle2: {}".format(
                angle1, angle2))

        # Correct angles to fit bounds.
        angle1 %= self.driver.max_angle
        angle2 %= self.driver.max_angle
        self.logger.debug(
            "Post-correction angles: angle1: {}, angle2: {}".format(
                angle1, angle2))

        # Test headings for valid 0,360 values.
        assert 0 <= angle1 <= 360, "angle1 is {}".format(angle1)
        assert 0 <= angle2 <= 360, "angle2 is {}".format(angle2)

        # Todo: Consider making this a function call.
        line_not_found = True
        while line_not_found:

            # Drives in each direction.
            self.driver.move(osc_speed, angle1)
            # Passes control to find line, which moves
            # until it finds line or runs out of time.
            # Note: watch_for_line returns "line_found"
            # (bool) and "time_elapsed" (int)
            results = self.watch_for_line(osc_time)
            self.driver.move(0, 0)

            if results["line_found"]:
                line_not_found = False

            # Search in other direction.
            self.driver.move(osc_speed, angle2)

            # "time elapsed" is used as max_time for more precise movements.
            results = self.watch_for_line(results["time_elapsed"] * 2)
            self.logger.debug(
                "Oscillation direction 1: osc_speed: {}, heading: {}".format(
                    osc_speed, heading))
            self.driver.move(0, 0)

            if results["line_found"]:
                line_not_found = False

            # If line is not found, Continue looping until line is found.
            # For now, stop when max speed is hit.
            osc_speed += 90
            if osc_speed >= self.driver.max_speed:
                line_not_found = False

    def reading_contains_pattern(self, pattern, reading):
        """Search the given reading for the given pattern.

        :param pattern: Pattern to search reading for.
        For example, [1, 1] for a pair of consecutive ones.
        :type pattern: list
        :param reading: IR array reading to search for the
        given pattern. Should contain only 0s and 1s.
        :type reading: list
        :returns: True if the pattern is in the reading, False otherwise.

        """
        return "".join(map(str, pattern)) in "".join(map(str, reading))

    def watch_for_line(self, max_time):
        """Recieves time period for which to continuously watch for line.
        Returns True when line is found.
        Returns False if line is not found before time is hit.
        """
        start_time = time()
        while True:
            reading = self.ir_hub.read_all()
            for name, array in reading.iteritems():
                if self.reading_contains_pattern([1, 1], array):
                    return {"line_found": True,
                            "time_elapsed": time() - start_time}
                if time() - start_time > max_time:
                    return {"line_found": False,
                            "time_elapsed": time() - start_time}
    @lib.api_call
    def assign_states(self, current_ir_reading=None):
        """ on_x=True flag does not allow intersection errors
            once left&right arrays clear intersection, on_x = false.
        Take 4x16 bit arrays and assigns the array to proper orientations.
        Note that the proper orientations are front, back, left and right.
        """
        # Keep prev back state to ignore large objects on back array
        prev_back_state = self.back_state
        # Get the current IR readings
        if current_ir_reading is None:
            current_ir_reading = self.ir_hub.read_binary(False)
        # Heading east
        if self.heading == 270:
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
        # Heading west
        elif self.heading == 90:
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
        elif self.heading == 180:
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
        elif self.heading == 0:
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

        #Clear on_x flag if off line on side arrays
        if(self.on_x and ((self.right_state > 15) or (self.left_state > 15))):
            self.on_x = False

        #Check for error conditions
        if((self.front_state > 15) or (self.back_state > 15) or
            (self.right_state < Follower.No_Line) and (self.left_state < Follower.No_Line)):
            
            if((self.right_state < 16) and (self.left_state < 16))and not self.on_x:
                # Found Intersection because left and right lit up
                # if on_x=True, ignore this error
                self.error = "ON_INTERSECTION" 
            if((self.front_state == Follower.Large_Object) ):
                # Found large object on front array. 
                self.error = "LARGE_OBJECT" 
            if( self.back_state == Follower.Large_Object):
                # Ignore large objects on back array by using prev back state
                self.back_state == prev_back_state
            if((self.front_state == Follower.No_Line) and (self.back_state == Follower.No_Line)):
                # Front and back lost line
                self.error = "LOST_LINE" 
            elif(self.front_state == Follower.No_Line):
                # Front lost line
                self.error = "FRONT_LOST" 
            elif(self.back_state == Follower.No_Line):
                # Back lost line
                self.error = "BACK_LOST" 
        else: #no errors
            self.error = "NONE" 

    def update_exit_state(self):
        if(self.error == "ON_INTERSECTION"):
            self.intersection = True
        elif(self.error == "LOST_LINE"):
            self.lost_line = True
        elif(self.error == "FRONT_LOST"):
            self.lost_line = True
        elif(self.error == "BACK_LOST"):
            self.lost_line = True
    #    elif(self.error == 5):
    #        self.lost_line = True

    def get_position_lr(self, readings):
        """Reading the IR sensors from left to right.

        Calculates the current state in reference to center from 
        left to right. States go form -15 to 15.

        """
        self.hit_position = []
        state = 0.0
        for index, value in enumerate(readings):
            if(value == 1):
               self.hit_position.append(index)
        if len(self.hit_position) >= 4:
            # Error: Large Object detected
            return Follower.Large_Object
        if len(self.hit_position) == 0:
            # Error: No line detected
            return Follower.No_Line

        state = self.hit_position[0] * 2
        #Use first two hit irs to determine position on array
        #Ignores extra bits as noise.
        if len(self.hit_position) > 1:
            if self.hit_position[1] > 0:
                state = state + 1
            if abs(self.hit_position[0] - self.hit_position[1]) > 1:
                # Error: Discontinuity in sensors
                return Follower.Noise
        state = state - 15
        return state

    def get_position_rl(self, readings):
        """Reading the IR sensors from right to left.

        Calculates the current state in reference to center from 
        right to left. States go form -15 to 15.

        """
        self.hit_position = []
        state = 0.0
        for index, value in enumerate(readings):
            if(value == 1):
               self.hit_position.append(index)
        if len(self.hit_position) >= 4:
            # Error: Large Object detected
            return Follower.Large_Object
        if len(self.hit_position) == 0:
            # Error: No line detected
            return Follower.No_Line

        state = self.hit_position[0] * 2
        #Use first two hit irs to determine position on array
        #Ignores extra bits as noise.
        if len(self.hit_position) > 1:
            if(self.hit_position[1] > 0):
                state = state + 1
            if(abs(self.hit_position[0] - self.hit_position[1]) > 1):
                # Error: Discontinuity in sensors
                return Follower.Noise
        state = (state - 15) * -1
        return state

    @lib.api_call
    def motors(self, bot_angle):
        """Used to update the motors speed and angular motion."""
        #If outside standard deviation angle, use rotate to straiten
        #if within std angle, use move to translate forward and strafe to
        # correct towards line horizontally
        # std is 7 on a range of -15 to 15
        std_angle = 7
        if abs(bot_angle) < std_angle:
            translate_angle = (self.strafe_error - self.heading + 180)%360
            self.driver.move(self.translate_speed, translate_angle) 
        else:
            #cap speed between (-100,100)
            rotate_speed = max(-100,min(100,self.rotate_error))
            self.logger.info("rotate_speed = {}".format(rotate_speed))
            self.driver.rotate(rotate_speed) 
            
    @lib.api_call
    def get_out_of_box(self):
      """Used to get the bot out of the box"""
      last_count = 0
      while True:
        count = 0
        ir_reading = self.ir_hub.read_binary(False)
        for value in ir_reading["back"]:
            if(value == 1):
                count += 1
        if((count != 0) and (last_count != 0)):
            self.driver.move(0,0)
            return "DONE"
        self.driver.move(70,0)
        self.logger.info("count = {}".format(count))
        last_count = count 



    @lib.api_call
    def center_on_intersection(self, heading = 180):
        """center on intersection"""
        side_to_side_strafe = pid_mod.PID()
        self.center_on_line(heading)
        previous_time = time();
        self.heading = heading
        while True:
            current_time = time()
            # Init front_PID
            side_to_side_strafe.set_k_values(3.75, 0, .75)
            # Assig states
            self.assign_states()
            # Call PID`
            bot_position = (self.left_state + self.right_state)/2
            # Call Rotate PID
            self.logger.info("bot_position = {}".format(bot_position))
            position_error = side_to_side_strafe.pid(
                0, bot_position, self.sampling_time)
            # Report errors from strafe and rotate pid's 
            if(abs(bot_position) < 3):
                self.driver.move(0,0)
                break
            # Cap at 0 and 100
            translate_speed =  max(0,min(100,abs(position_error)))
            if(position_error >= 0):
                translate_angle = 0
            else:
                translate_angle = 180
            if(abs(bot_position) < 3):
              return
            self.logger.info("translate_speed = {}".format(translate_speed))
            self.logger.info("translate_angle = {}".format(translate_angle))
            self.driver.move(translate_speed, translate_angle)
            # Take the current time set it equal to the previous time
            previous_time = current_time
        return "DONE"


    @lib.api_call
    def center_on_line(self, heading = 180):
        """Used to center on the line"""
        center_rotate_pid = pid_mod.PID()
        side_to_side_strafe = pid_mod.PID()
        previous_time = time();
        self.heading = heading
        while True:
            center_rotate_pid.integral_error = 0
            while True:
                current_time = time()
                # Init front_PID
                center_rotate_pid.set_k_values(3.75, 0, .75)
                # Assig states
                self.assign_states()
                # Check for error conditions
                self.sampling_time = current_time - previous_time
                # Call PID`
                bot_angle = (self.front_state - self.back_state)
                # Call Rotate PID
                self.logger.info("bot_angle = {}".format(bot_angle))
                rotate_error = center_rotate_pid.pid(
                    0, bot_angle, self.sampling_time)
                # Report errors from strafe and rotate pid's 
                if(abs(bot_angle) < 3):
                  self.driver.move(0,0)
                  break
                self.logger.info("rotate_error = {}".format(rotate_error))
                rotate_speed = max(-100,min(100,rotate_error))
                self.driver.rotate(rotate_speed)
                # Take the current time set it equal to the previous time
                previous_time = current_time
            side_to_side_strafe.integral_error = 0
            while True:
                current_time = time()
                # Init front_PID
                side_to_side_strafe.set_k_values(3.75, 0, .75)
                # Assig states
                self.assign_states()
                # Call PID`
                bot_position = (self.front_state + self.back_state)/2
                # Call Rotate PID
                self.logger.info("bot_position = {}".format(bot_position))
                position_error = side_to_side_strafe.pid(
                    0, bot_position, self.sampling_time)
                # Report errors from strafe and rotate pid's 
                if(abs(bot_position) < 3):
                    self.driver.move(0,0)
                    break
                # Cap at 0 and 100
                translate_speed =  max(0,min(100,abs(position_error)))
                if(position_error >= 0):
                    translate_angle = 90
                else:
                    translate_angle = 270
                if(abs(bot_position) < 3):
                  return
                self.logger.info("translate_speed = {}".format(translate_speed))
                self.logger.info("translate_angle = {}".format(translate_angle))
                self.driver.move(translate_speed, translate_angle)
                # Take the current time set it equal to the previous time
                previous_time = current_time
            if((abs(self.front_state) < 3) and (abs(self.back_state < 3))):
                return "Done"

    @lib.api_call
    def center_on_blue_block(self, heading=180):
        # Assumes Front array (from heading) is on blue block
        self.heading = heading
        # Assign the current states to the correct heading
        self.assign_states()
        # Move forward until off block
        direction = 180 - heading
        while self.front_state == Follower.Large_Object:
            self.driver.move(60,direction)
            self.assign_states()
        #After off block, use center on line to straigten
        self.center_on_line(heading)
        return "DONE CENTER ON BLUE BLOCK"





    @lib.api_call
    def center_on_red(self):
        return True  # TODO: Actually center on red_block





 
