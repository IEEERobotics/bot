"""Encapsulates functionality required to operate the Simon Says Servo hardware."""

import time
from math import pi

import bot.lib.lib as lib
from bot.hardware.stepper_motor import Stepper_motor
from bot.hardware.servo import Servo

class SimonSaysHardware(object):

    """Simon Says manipulator that encapsulates servo and stepper"""

    def __init__(self):
        """Build logger, get config, build stepper and servo."""

        # Load and store logger
        self.logger = lib.get_logger()

        # Load and store configuration dict
        self.config = lib.get_config()

        # Variable that stores the current position of the Simon
        # says hardware.At startup it's set to 1.
        self.position = 1
        
        if self.config["test_mode"]["simon_player"]:
            # add code for test mode
            pass

        else:
            # Build the servo and stepper motor
            self.servo = Servo(self.config["simon"]["servo"])
            self.stepper = Stepper_motor(
                self.config["simon"]["stepper"])

        # TODO(Vijay): Should add position property 
        """Getter for motor's current position.

        :returns: Position of the motor.

        """

        """Setter for the motor's current position. Call it each time
        the hardware rotates. HAS to be in the range 1-4.

        1 - 0 degrees
        2 - 90 degrees
        3 - 180 degrees
        4 - 360 degrees

        :param pos: new position of the motor.
        :type speed: int

        """

    def turn(self, position):
        """ Sets the servo to the specified position, according to the
        numbers mapped above. Then actuates the servo to press buttons.

        :param position: rotates to the desired position.
        :type position: int ranging from 1 - 4.

        """
        if ((position > 0) or (position < 5)):
            # count the number of 90 degree rotations to be made.
            count = position - self.position

            # DEBUG
            print "The no. of c-clockwise movements : {}".format(count)

            if count > 0:
                # rotate the specified number of times counterclockwise
                for i in range(0, count):
                    self.stepper.rotate_90_counter_clockwise()

            elif count < 0:
                count = -count
                # rotate the specified number of times clockwise
                for i in range(0, count):
                    self.stepper.rotate_90_clockwise()

            # change the current position to the new position
            self.position = position

            # actuate the servo rails to press the button - to be tested
            self.servo.position = 180

            # TODO (Vijay): Put the thread to sleep for a little bit.
            time.sleep(1)

            # Servo is reset to initial position
            self.servo.position = 90

    def press_start(self):
        """ Actuates the servo to press the start button.

        """
        self.servo.position = 0

        time.sleep(1)

        # Servo is reset to initial position
        self.servo.position = 90
