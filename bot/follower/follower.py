"""Logic for line following."""

import sys
from time import time
from time import sleep
import numpy as np

import bot.lib.lib as lib
import bot.hardware.ir_hub as ir_hub_mod
import bot.driver.mec_driver as mec_driver_mod
import pid as pid_mod
import bot.hardware.color_sensor as color_sensor_mod

from error_cases import LineLostError

class Follower(object):

    """Follows a line, detects intersections and stop conditions."""

    # Class variables
    # Array_Conditions
    Large_Object = 17  # the array sees a large object
    No_Line = 16  # the array see no line
    Noise = 19  # white values not next to each other

    # Variables for read_binary calls
    White_Black = True  # False  # True= white line, False= black line
    set_speed = 50

    THRESH = 60

    def __init__(self):
        # Build logger
        self.logger = lib.get_logger()

        # Build subsystems
        self.ir_hub = ir_hub_mod.IRHub()
        self.ir_hub.thrsh = 100
        self.driver = mec_driver_mod.MecDriver()
        self.color_sensor = color_sensor_mod.ColorSensor()

        # Build PIDs
        # FIXME 1 no longer in use
        self.front_right = pid_mod.PID();
        self.front_right_error = 0.0
        self.front_left = pid_mod.PID();
        self.front_left_error = 0.0
        self.back_right = pid_mod.PID();
        self.back_right_error = 0.0
        self.back_left = pid_mod.PID();
        self.back_left_error = 0.0
        self.strafe = pid_mod.PID()
        self.strafe_error = 0.0
        self.rotate_pid = pid_mod.PID()
        self.rotate_error = 0.0
        self.error = "NONE"

        # motor variables
        # FIXME 2 same as before
        self.translate_speed = 75
        self.prev_rate = 0

        # state variables
        self.heading = None  # must be initialize by caller
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
    def set_translate_speed(self, speed):
        self.translate_speed = speed

    @lib.api_call
    def update(self):
        """Read IR values, compute aggregates."""
        ir_readings = self.ir_hub.read_binary(Follower.White_Black)
        for name, reading in ir_readings.iteritems():
            reading_arr = np.int_(reading)  # convert readings to numpy array
            reading_sum = np.sum(np_reading)  # = no. of units lit
            if reading_sum > 0:
                self.ir_agg[name] = (
                    np.sum(self.ir_pos * reading_arr) / reading_sum)
            else:
                self.ir_agg[name] = None
        self.timeLastUpdated = time.time()

    @lib.api_call
    def get_strafe_error(self):
        return self.strafe_error

    @lib.api_call
    def get_rotate_error(self):
        return self.rotate_error

    def reset_errors(self):
        self.error = "NONE"
        # state variables
        # self.front_state = Follower.No_Line
        # self.back_state = Follower.No_Line
        # self.left_state = Follower.No_Line
        # self.right_state = Follower.No_Line

        # post error vars
        self.intersection = False
        self.lost_line = False
        self.timeLastUpdated = -1.0
        self.strafe_error = 0.0
        self.rotate_error = 0.0

        # reset pids
        self.strafe.clear_error()
        self.rotate_pid.clear_error()
        return

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
    def oscillate(self, heading=0, osc_time=0.5):
        """Oscillate sideways, increasing in amplitude until line is found
        :param heading: The forward direction of the bot.
        :param osc_time: The initial time spent in each direction.

        """

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

        # Heading may be unecessary.
        # # Test headings for valid 0,360 values.
        # assert 0 <= angle1 <= 360, "angle1 is {}".format(angle1)
        # assert 0 <= angle2 <= 360, "angle2 is {}".format(angle2)

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
        # Keep prev front to ignore noise conditions
        # Keep prev back state to ignore large objects on back array
        prev_front_state = self.front_state
        prev_back_state = self.back_state
        # Get the current IR readings
        if current_ir_reading is None:
            current_ir_reading = self.ir_hub.read_binary(Follower.White_Black)

        # using heading, make front/back/left/right state assignments
        self.determine_states(current_ir_reading)

        # Clear on_x flag if off line on side arrays
        if(self.on_x and ((self.right_state > 15) or (self.left_state > 15))):
            self.on_x = False

        # Check for error conditions
        if((self.front_state > 15) or (self.back_state > 15) or
            (self.right_state < Follower.No_Line) and
                (self.left_state < Follower.No_Line)):

            # Lost Lines Superscede other conditions
            if((self.front_state == Follower.No_Line) and
                    (self.back_state == Follower.No_Line)):
                # Front and back lost line
                self.error = "LOST_LINE"
            elif(self.front_state == Follower.No_Line):
                # Front lost line
                self.error = "FRONT_LOST"
            elif(self.back_state == Follower.No_Line):
                # Back lost line
                self.error = "BACK_LOST"
            # Intersection preceds Large Object
            elif ((not (self.right_state == Follower.No_Line) and
                    not (self.left_state == Follower.No_Line)) and
                    not self.on_x):
                # Found Intersection because left and right lit up
                # if on_x=True, ignore this error
                self.error = "ON_INTERSECTION"
            elif((self.front_state == Follower.Large_Object)):
                # Found large object on front array.
                self.error = "LARGE_OBJECT"
            else:
                if(self.back_state == Follower.Large_Object):
                    # Ignore large objects on back array
                    # by using prev back state
                    self.back_state = prev_back_state
                if(self.front_state == Follower.Noise):
                    # Ignore Noise conditions
                    self.front_state = prev_front_state
                if(self.back_state == Follower.Noise):
                    # Ignore Noise conditions
                    self.back_state = prev_back_state

                    # self.error = "NONE"
        else:  # no errors
            self.error = "NONE"

        self.logger.info("FS: {}, BS {}, LS {}, RS {}".format(
            self.front_state,
            self.back_state,
            self.left_state,
            self.right_state))
        return self.front_state, self.back_state, \
            self.left_state, self.right_state

    def determine_states(self, current_ir_reading):
        if self.heading is None:
            self.heading = 180  # use implicit default value for testing
            self.logger.info("Using Test Heading = 180")
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
            # self.left_state = self.get_position_lr(
            #    current_ir_reading["left"])
            # right is on the right
            self.right_state = self.get_position_rl(
                current_ir_reading["right"])
            # for tri_state, copy right state to left
            self.left_state = self.right_state
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
            # self.right_state = self.get_position_rl(
            #    current_ir_reading["left"])
            # in tri state, copy left to right
            self.right_state = self.left_state

    def update_exit_state(self):
        if(self.error == "ON_INTERSECTION"):
            self.intersection = True
        elif(self.error == "LOST_LINE"):
            self.lost_line = True
        elif(self.error == "FRONT_LOST"):
            self.lost_line = True
        elif(self.error == "BACK_LOST"):
            self.lost_line = True

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
        # Use first two hit irs to determine position on array
        # Ignores extra bits as noise.
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
        # Use first two hit irs to determine position on array
        # Ignores extra bits as noise.
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
        # If outside standard deviation angle, use rotate to straiten
        # if within std angle, use move to translate forward and strafe to
        # correct towards line horizontally
        # std is 7 on a range of -15 to 15
        std_angle = 7
        if abs(bot_angle) < std_angle:
            translate_angle = (self.strafe_error - self.heading + 180) % 360
            self.driver.move(self.translate_speed, translate_angle)
        else:
            # cap speed between (-100, 100)
            rotate_speed = max(-100, min(100, self.rotate_error))
            self.logger.info("rotate_speed = {}".format(rotate_speed))
            self.rotate(rotate_speed)

    @lib.api_call
    def smart_jerk(self):
        """Used to get the bot out of the box"""
        last_count = 0
        while True:
            count = 0
            ir_reading = self.ir_hub.read_binary(Follower.White_Black)
            for value in ir_reading["back"]:
                if(value == 1):
                    count += 1
            if((count != 0) and (last_count != 0)):
                self.driver.move(0, 0)
                return "DONE"
            self.driver.move(self.translate_speed, 0)
            self.logger.info("count = {}".format(count))
            last_count = count

    # Prevent rapid sign changes in rotate calls
    def rotate(self, rate):
        if(self.prev_rate*rate < 0):
            self.driver.move(0, 0)
            sleep(0.2)
        self.prev_rate = rate
        self.driver.rotate(rate)
        return

    @lib.api_call
    def center_on_intersection(self, heading=180):
        """center on intersection"""
        # first use center on line
        self.heading = heading
        self.center_on_line(heading)

        # then correct forwards/backwards
        forw_to_back_strafe = pid_mod.PID()
        # Init front_PID
        forw_to_back_strafe.set_k_values(5.5, 0.5, 2)
        previous_time = time()
        while True:
            # kill momentum before reading
            self.driver.move(0, 0)
            # Assig states
            self.assign_states()
            # Check for error conditions
            if ((self.error != "NONE" and self.error != "ON_INTERSECTION")
                or (self.left_state == Follower.No_Line
                    or self.right_state == Follower.No_Line)):
                self.update_exit_state()
                self.logger.info("Error: {}".format(self.error))
                self.logger.info("FS: {}, BS: {}, lS: {}, RS: {}".format(
                    self.front_state,
                    self.back_state,
                    self.left_state,
                    self.right_state))
                self.driver.move(0, 0)
                return self.error
            # setup pid
            bot_front_position = (self.left_state + self.right_state)/2
            current_time = time()
            # Call PID
            self.logger.info("bot_front_position = {}".format(bot_front_position))
            position_error = forw_to_back_strafe.pid(
                0, bot_front_position, self.sampling_time)
            if(abs(bot_front_position) < 3):
                self.driver.move(0, 0)
                break
            # Cap at 0 and 100
            translate_speed = max(0, min(100, abs(position_error)))
            # use sign and heading to determin which direction to strafe
            if(position_error >= 0):
                translate_angle = (0 + self.heading) % 360
            else:
                translate_angle = (180 + self.heading) % 360
            if(abs(bot_front_position) < 5):
                return
            self.logger.info("translate_speed = {}".format(translate_speed))
            self.logger.info("translate_angle = {}".format(translate_angle))
            self.driver.move(translate_speed, translate_angle)
            # Take the current time set it equal to the previous time
            previous_time = current_time
        return "DONE"

    @lib.api_call
    def center_on_line(self, heading=180):
        """Used to center on the line"""
        center_rotate_pid = pid_mod.PID()
        side_to_side_strafe = pid_mod.PID()
        self.heading = heading
        while True:
            center_rotate_pid.clear_error()
            previous_time = time()
            # Init front_PID
            center_rotate_pid.set_k_values(6.75, .4, 1.75)
            while True:
                # kill momentum before reading
                self.driver.move(0, 0)
                # Assig states
                self.assign_states()
                # Check for error conditions
                if(self.error != "NONE" and self.error != "ON_INTERSECTION"):
                    self.update_exit_state()
                    self.logger.info("Error: {}".format(self.error))
                    self.logger.info("FS: {}, BS: {}, lS: {}, RS: {}".format(
                        self.front_state,
                        self.back_state,
                        self.left_state,
                        self.right_state))
                    self.driver.move(0, 0)
                    return self.error

                current_time = time()
                self.sampling_time = current_time - previous_time
                bot_angle = (self.front_state - self.back_state)
                # Call Rotate PID
                self.logger.info("bot_angle = {}".format(bot_angle))
                rotate_error = center_rotate_pid.pid(
                    0, bot_angle, self.sampling_time)
                # Report errors from strafe and rotate pid's
                if(abs(bot_angle) < 4):
                    self.driver.move(0, 0)
                    break
                self.logger.info("rotate_error = {}".format(rotate_error))
                rotate_speed = max(-100, min(100, rotate_error))
                self.rotate(rotate_speed)
                # Take the current time set it equal to the previous time
                previous_time = current_time

            side_to_side_strafe.clear_error()
            previous_time = time()
            # Init front_PID
            side_to_side_strafe.set_k_values(4.75, 2, 5.75)
            while True:
                # kill momentum before reading
                self.driver.move(0, 0)
                # Assig states
                self.assign_states()
                # Check for error conditions
                if(self.error != "NONE" and self.error != "ON_INTERSECTION"):
                    self.update_exit_state()
                    self.logger.info("Error: {}".format(self.error))
                    self.logger.info("FS: {}, BS: {}, lS: {}, RS: {}".format(
                        self.front_state,
                        self.back_state,
                        self.left_state,
                        self.right_state))
                    self.driver.move(0, 0)
                    return self.error
                # if angle off, break to rotate again
                bot_angle = (self.front_state - self.back_state)
                if(bot_angle >= 4):
                    break
                # calculate PID terms`
                current_time = time()
                bot_front_position = (self.front_state + self.back_state)/2
                # Call side_to_side PID
                self.logger.info("bot_front_position = {}".format(bot_front_position))
                self.sampling_time = current_time - previous_time
                position_error = side_to_side_strafe.pid(
                    0, bot_front_position, self.sampling_time)
                # Report errors from strafe and rotate pid's
                if(abs(bot_front_position) < 3):
                    self.driver.move(0, 0)
                    break
                # Cap at 0 and 100
                translate_speed = max(0, min(100, abs(position_error)))
                # use sign and heading to determine which side to strafe to
                if(position_error >= 0):
                    translate_angle = (-90 + self.heading) % 360
                else:
                    translate_angle = (-270 + self.heading) % 360
                if(abs(bot_front_position) < 3):
                    return
                    self.logger.info(
                        "position_error = {}".format(
                            position_error))
                    self.logger.info(
                        "translate_speed = {}".format(
                            translate_speed))
                    self.logger.info(
                        "translate_angle = {}".format(
                            translate_angle))
                    self.driver.move(translate_speed, translate_angle)
                # Take the current time set it equal to the previous time
                previous_time = current_time

            if((abs(self.front_state) < 4) and (abs(self.back_state < 4))):
                return "Done"
        # end top while loop

    @lib.api_call
    def get_result(self):
        self.assign_states()
        return self.error

    @lib.api_call
    def strafe_to_line(self, heading=90):
        """Attempt to strafe sideways from one firing line to the next  """
        # assumes centered on line
        self.heading = heading
        self.assign_states()
        # strafe until off current line
        while ((self.left_state < Follower.No_Line) and
                (self.right_state < Follower.No_Line)):
            self.driver.move(self.translate_speed, heading)
            self.assign_states()
            self.driver.move(0, 0)
        # strafe until on next line
        while ((self.left_state == Follower.No_Line) or
                (self.right_state == Follower.No_Line)):
            self.driver.move(self.translate_speed, heading)
            self.assign_states()
            self.driver.move(0, 0)
        return "DONE STRAFING TO LINE"
        
    @lib.api_call
    def analog_state(self):
        """Make call to analog arrays"""

        # Take current time before reading ADC readings of the IRs
        previous_time = time()
        self.front_right.set_k_values(kp = .2, kd = 0.1, ki = 0.0)
        self.front_left.set_k_values(kp = .2, kd = 0.1, ki = 0.0)

        self.back_right.set_k_values(kp = .03, kd = 0.009, ki = 0.0)
        self.back_left.set_k_values(kp = .03, kd = 0.009, ki = 0.0)
        self.front_bin = [[0 for x in range(8)] for y in range(3)]

        self.front_right_error = 0.0
        self.front_left_error = 0.0
        self.back_right_error = 0.0
        self.back_left_error = 0.0
        left_count = 0
        right_count = 0

        while True:
            # Read ir arrays
            self.array_block = self.ir_hub.read_all()
            self.normalize_arrays()
            self.track_position()

            # Get the current time of the CPU
            current_time = time()
            self.sampling_time = current_time - previous_time

            # time before reading the IRs
            previous_time = time()

            # Count the number of hits
            front_hits = self.count_num_of_hits(self.array_block["front"])
            back_hits  = self.count_num_of_hits(self.array_block["back"])
            right_hits = self.count_num_of_hits(self.array_block['right'])
            left_hits  = self.count_num_of_hits(self.array_block['left'])

            self.front_bin[2] = self.front_bin[1]
            self.front_bin[1] = self.front_bin[0]
            self.front_bin[0] = self.assign_bin(self.array_block["front"])

            # print "fornt hits {}".format(self.front_bin[0])
            #right_hits = self.count_num_of_hits(self.array_block["right"])
            #left_hits = self.count_num_of_hits(self.array_block["left"])
            #print self.array_block

            #if not front_hits > 1:
            #    if((self.front_bin[1][0] == 1 \
            #        and self.front_bin[1][1] == 1) \
            #        or (self.front_bin[2][0] == 1 \
            #            and self.front_bin[2][1] == 1)):
            #        self.driver.move(0,0)
            #        return "left turn"

            #    if((self.front_bin[0][7] == 1 \
            #        and self.front_bin[1][7] == 1) \
            #        or (self.front_bin[0][6] == 1 \
            #        and self.front_bin[1][6] == 1)):
            #        self.driver.move(0,0)
            #        return "right turn"

            if front_hits > 4 or back_hits > 4 or right_hits > 2 or left_hits > 2:
                self.driver.move(60,180)
                sleep(.001)
                self.driver.move(0,0)
                return "block or t-intersection"

            #else:
            #    if((self.front_bin[1][0] == 1 \
            #        and self.front_bin[1][1] == 1) \
            #        or (self.front_bin[2][0] == 1 \
            #            and self.front_bin[2][1] == 1)):
            #        self.driver.move(0,0)
            #        return "left turn at intersection"
            #    if((self.front_bin[0][7] == 1 \
            #        and self.front_bin[1][7] == 1) \
            #        or (self.front_bin[0][6] == 1 \
            #            and self.front_bin[1][6] == 1)):
            #        self.driver.move(0,0)
            #        return "right turn at intersection"

            if back_hits == 0 and front_hits == 0:
                self.driver.move(speed = 0, angle = 0)
                print "lost line"
                raise LineLostError("reading: {}".format(
                                        self.array_block()))

            if(front_hits > 0):
                # Call PID
                self.front_right_error = (50 + self.front_right.pid(
                    0, self.bot_front_position, self.sampling_time))

                # Call PID
                self.front_left_error = (50 - self.front_left.pid(
                    0, self.bot_front_position, self.sampling_time))

                if(self.front_right_error >= 80):
                    self.front_right_error = 80
                elif(self.front_right_error <= -80):
                    self.front_right_error = -80

                if(self.front_left_error >= 80):
                    self.front_left_error = 80
                elif(self.front_left_error <= -80):
                    self.front_left_error = -80
            else:
                self.front_right_error = (50 + self.front_right.pid(
                    0, self.bot_back_position, self.sampling_time))

                # Call PID
                self.front_left_error = (50 - self.front_left.pid(
                    0, self.bot_back_position, self.sampling_time))

                if(self.front_right_error >= 80):
                    self.front_right_error = 80
                elif(self.front_right_error <= -80):
                    self.front_right_error = -80

                if(self.front_left_error >= 80):
                    self.front_left_error = 80
                elif(self.front_left_error <= -80):
                    self.front_left_error = -80

            if(back_hits > 0):
                # Call PID
                self.back_right_error = (50 + self.back_right.pid(
                    0, self.bot_back_position, self.sampling_time))

                # Call PID
                self.back_left_error = (50 - self.back_left.pid(
                    0, self.bot_back_position, self.sampling_time))

                if(self.back_right_error >= 80):
                    self.back_right_error = 80
                elif(self.back_right_error <= -80):
                    self.back_right_error = -80

                if(self.back_left_error >= 80):
                    self.back_left_error = 80
                elif(self.back_left_error <= -80):
                    self.back_left_error = -80
            else:
                # Call PID
                self.back_right_error = self.set_speed + \
                    self.back_right.pid(0, self.bot_front_position, self.sampling_time)

                # Call PID
                self.back_left_error = self.set_speed - \
                    self.back_left.pid(0, self.bot_front_position, self.sampling_time)

                if(self.back_right_error >= 80):
                    self.back_right_error = 80
                elif(self.back_right_error <= -80):
                    self.back_right_error = -80

                if(self.back_left_error >= 80):
                    self.back_left_error = 80
                elif(self.back_left_error <= -80):
                    self.back_left_error = -80

            self.driver.set_motor(name = "front_right",
                                 value = self.front_right_error)
            self.driver.set_motor(name = "front_left",
                                 value = self.front_left_error)
            self.driver.set_motor(name = "back_right",
                                 value = self.back_right_error)
            self.driver.set_motor(name = "back_left",
                                 value = self.back_left_error)

    def normalize_arrays(self):
        """Uesd to mormaliza ir readings coming form the ir array"""
        for array in self.array_block:
            for position,value in enumerate(self.array_block[array]):
                self.array_block[array][position] = (255 - value) - 100
                if(self.array_block[array][position] < 0):
                    self.array_block[array][position] = 0

    def track_position(self):
        """Trak the positon of the line"""
        self.bot_front_position = 0;
        self.bot_back_position = 0;
        value = max(self.array_block["front"])
        if not (value < 10):
            index = self.array_block["front"].index(value)
            #if value > 10:
            if index < 4:
                self.bot_front_position = 5.0 * (4.0 - index) \
                                    * (4.0 - index) * (4.0 - index)
            else:
                self.bot_front_position = 5.0 * (3.0 - index) \
                                    * (3.0 - index) * (3.0 - index)

        value = max(self.array_block["back"])
        if not(value < 10):
            index = self.array_block["back"].index(value)
            #print value
            #if value > 10:
            if index < 4:
                self.bot_back_position = 5.0 * (4.0 - index) \
                                    * (4.0 - index) * (4.0 - index)
            else:
                self.bot_back_position = 5.0 * (3.0 - index) \
                                    * (3.0 - index) * (3.0 - index)

    def count_num_of_hits(self, array):
        count = 0
        for value in array:
            if value > 90:
                count = count + 1
        return count

    def assign_bin(self,a_array):
        array = [0,0,0,0,0,0,0,0]
        for index,value in enumerate(a_array):
            if value > self.THRESH:
                array[index] = 1
        return array

    @lib.api_call
    def check_for_branch(self, side):
        """Checks to see if there is a branch on the left.
        :returns: True or False
        """
        array_block = self.ir_hub.read_all()
        s_array = array_block[side]

        hits = self.count_num_of_hits(s_array)
        
        if hits <= 6:
            return True
        return False       
        
    @lib.api_call
    def is_intersection(self):
        """Determines whether an anomaly is a turn or an intersection.
        """
        if (self.check_for_branch("right") \
                or self.check_for_branch("left"))\
            and self.check_for_branch("front"):
            return True
        return False

    @lib.api_call
    def find_dir_of_int(self):
        if not (
            (self.check_for_branch("right") \
                or self.check_for_branch("left"))\
            and self.check_for_branch("front")):
           return "error: not intersection"

        elif self.check_for_branch("right")\
            and self.check_for_branch("left"):
            return "error: branches in both dirs.111"
        
        elif self.check_for_branch("right"):
            return "right"

        elif self.check_for_branch("left"):
            return "left"
  
    @lib.api_call
    def find_dir_of_turn(self):
        """Determines whether a turn is on the right or left
        :returns: right, left, intersection, error
        """
        
        if (self.check_for_branch("right") \
            and self.check_for_branch("left")):
            return "error: too many intersections"

        elif not self.check_for_branch("right") \
            and not self.check_for_branch("left"):
            return "error: no branches"

        elif (self.check_for_branch("right") \
                or self.check_for_branch("left"))\
            and self.check_for_branch("front"):
            return "intersection"

        elif  self.check_for_branch("right"):
            return "right"

        elif self.check_for_branch("left"):
            return "left"

        else:
            return "error: No condition found. Line lost."

    @lib.api_call
    def is_centerred_on_line(self):
        """Checks to see if bot is reasonably within center line.
        """
        arr_block = self.ir_hub.read_all()
        if arr_block['front'][4] < self.THRESH \
            or arr_block['front'][5] < self.THRESH:
            return True
        return False 
        
    @lib.api_call
    def follow_ignoring_turns(self):
        while True:
            self.recover()
            try:
                state = self.analog_state()
                print "Ir array reading"
                print self.ir_hub.read_all() 
                # Inch forward to be square on int
                # self.driver.jerk(speed=60,angle=0,duration=0.1)
                turn_dir = self.find_dir_of_turn()
                if turn_dir == "right" or turn_dir == "left":
                    self.driver.drive(60,0,0.1) 
                    self.rotate_to_line(turn_dir)
                    # self.driver.rough_rotate_90(turn_dir, r_time=0.6)
                    # Move out of intersection
                    self.recover()
                    self.driver.drive(60, angle=0, duration=0.09) 
                    self.recover()
                else:
                    self.recover()
            except LineLostError:
                self.logger.error("Line lost, attempting to recover")
                self.recover()


    @lib.api_call
    def rotate_to_line(self, direction, speed=50):
        """Rotates in given direction until line is found."""

        # Correct speed to match direction
        if direction == "right":
            speed = -speed

        self.driver.rotate(speed)
        sleep(0.3) # allow time to leave current intersection
         
        while not self.is_centerred_on_line():
            self.logger.debug("looking for line")
        
        # throw in hard reverse to stop immediately
        self.driver.rotate(-speed)
        sleep(0.05)
        self.driver.rotate(0)

    @lib.api_call
    def drive_to_line(self, speed=50, angle=0):
        """Drives in certain direction blindly until line is found."""

        self.driver.move(speed,angle)
        while not self.is_centerred_on_line():
            self.logger.debug("looking for line")

        self.driver.hard_stop(speed,angle)
    
    @lib.api_call
    def recover(self):
        """When recovery is needed, this function continually calls itself until problem is solved.
        """

        readings = self.ir_hub.read_all()
        
        # Terminating condition.
        # Lined up on line normally.
        if self.check_for_branch('front'):
            self.logger.debug("successfully recovered to line")
            return True

        # Front sees line, one of sides does.
        elif self.check_for_branch('front') and not self.check_for_branch('back') \
                and self.check_for_branch('right') and not self.check_for_branch('left'):
            self.logger.debug("recovering from crooked alignment, line on right")
            self.drive_to_line(50, 90)
            self.recover()
        elif self.check_for_branch('front') and not self.check_for_branch('back') \
                and not self.check_for_branch('right') and self.check_for_branch('left'):
            self.logger.debug("recovering from crooked alignment, line on right")
            self.drive_to_line(50, -90)
            self.recover()

        # Sides see line but front/back do not
        elif not self.check_for_branch('front') and not self.check_for_branch('back') \
                and self.check_for_branch('right') and not self.check_for_branch('left'):
            self.logger.debug("Sides see line but front/back do not")
            self.rotate_to_line('right')
            self.recover()
        elif not self.check_for_branch('front') and not self.check_for_branch('back') \
                 and not self.check_for_branch('right') and self.check_for_branch('left'):
            self.logger.debug("Sides see line but front/back do not")
            # Todo: Store history of readings to intelligently pick dir instead of guess.
            self.rotate_to_line('left')
            self.recover()

        # Front has lost line, use sides to recover
        elif not self.check_for_branch('front') and self.check_for_branch('left') \
              and not self.check_for_branch('right'):
            self.logger.debug("Front has lost lines, using sides to recover")
            self.rotate_to_line('left')
            self.recover()
        elif not self.check_for_branch('front') and not self.check_for_branch('left') \
              and self.check_for_branch('right'):
            self.logger.debug("Front has lost lines, using sides to recover")
            self.rotate_to_line('right')
            self.recover()

        # Front sees something big, side's do not.
        # most likely on turn/int, but sides not over it yet.
        # inch forward.
        elif self.count_num_of_hits(readings['front']) < 6 \
                and not self.check_for_branch('left') and not self.check_for_branch('right'):
            self.logger.debug("Front sees something big, side's do not, inch fwd.")
            sleep(0.1)
            self.driver.drive(60,0,0.1)
            self.recover()

        # Back sees large object, sides see nothing.
        elif self.check_for_branch('back') \
             and not self.check_for_branch('front')\
             and not self.check_for_branch('left') and not self.check_for_branch('right'):
            self.logger.debug(
                    "Back sees large ({}) object, sides see nothing. Inch bkwd.".format(
                            self.count_num_of_hits(readings['back'])))
            self.driver.drive(60,180,0.1)
            self.recover()


