"""Abstraction layer for stepper motors."""

import bot.lib.lib as lib
import time
import bbb.gpio as gpio
import threading

class Stepper_motor(object):

    """Class for abstracting stepper motor settings."""

    def __init__(self):
        """Setup GPIO interface.
        
        """

        # TODO(kvijay1995): After testing the motor, add logger,
        # config for testing, and add pins to config.yaml
        # Implement the helper functions.

        # Build the GPIO pins in live mode

        # Build logger
        self.logger = lib.get_logger()

        self.gpio_1 = gpio.GPIO(8)
        self.gpio_2 = gpio.GPIO(78)
        self.gpio_3 = gpio.GPIO(76)
        self.gpio_4 = gpio.GPIO(74)

    def clockwise(self): 
        """The motor rotates clockwise.

        TODO(kvijay1995) : Needs to be tested.

        """
        self.gpio_1.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_1.set_value(1)
        self.gpio_2.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_3.set_value(1)
        self.gpio_4.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_4.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_4.set_value(1)
        time.sleep(1.0/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(1)
        time.sleep(1.0/10000.0)

        self.gpio_1.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(1)
        time.sleep(1.0/10000.0)

    def counter_clockwise(self): 
        """Rotates the motor counter clockwise

        TODO(kvijay1995): Needs to be tested.

        """
        self.gpio_4.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_4.set_value(1)
        self.gpio_3.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_2.set_value(1)
        self.gpio_1.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_1.set_value(0)
        time.sleep(1.0/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_1.set_value(1)
        time.sleep(1.0/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(1)
        time.sleep(1.0/10000.0)

        self.gpio_4.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(1)
        time.sleep(1.0/10000.0)

    @property
    def speed(self):
        """Getter for motor's current speed.

        :returns: Speed of the motor.

        """

    @speed.setter
    def speed(self, speed):
        """Setter for the motor's speed.

        :param speed: Speed of motor rotation.
        :type speed: int

        """

    def rotate_90_clockwise(self):
        """Rotates the motor 90 degrees in the 
        clockwise direction.

        """
        for i in range(0,128):
            self.clockwise()

    def rotate_90_counter_clockwise(self):
        """Rotates the motor 90 degrees in the
        counter_clockwise direction.

        """
        for i in range(0,128):
            self.counter_clockwise()

    @lib.api_call
    def test(self):
        """Test function for the motor."""
        self.rotate_90_clockwise()
        self.rotate_90_counter_clockwise()
