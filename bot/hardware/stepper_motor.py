"""Abstraction layer for stepper motors."""

import time
import pybbb.bbb.gpio as gpio
import threading

class Stepper_motor(object):

    """Class for abstracting stepper motor settings."""

    def __init__(self, gpio_1, gpio_2, gpio_3, gpio_4):
        """Setup GPIO interface.

        :param gpio_1, gpio_2, gpio_3, gpio_4: The four GPIO
        pins used by this stepper motor.

        :type gpio_* = int

        """

        # TODO(kvijay1995): After testing the motor, add logger,
        # config for testing, and add pins to config.yaml
        # Implement the helper functions.

        # Build the GPIO pins in live mode
        self.gpio_1 = gpio.GPIO(8)
        self.gpio_2 = gpio.GPIO(78)
        self.gpio_3 = gpio.GPIO(76)
        self.gpio_4 = gpio.GPIO(74)

        # Build the different threads required to rotate the motor
        self.t1 = threading.Thread(
            target = gpio_1.pulse, args = (3.0/1000.0))

        self.t2 = threading.Thread(
            target = gpio_2.pulse, args = (3.0/1000.0))

        self.t3 = threading.Thread(
            target = gpio_3.pulse, args = (3.0/1000.0))

        self.t4 = threading.Thread(
            target = gpio_4.pulse, args = (3.0/1000.0))

    def clockwise(self, duration = 10):
        """The motor rotates clockwise.

        :param duration: duration to spin the motor.

        TODO(kvijay1995) : Needs to be tested.

        """

        start = time.time()

        while time.time() - start < duration:
            t1.start()
            time.sleep(2.0/1000.0)

            t2.start()
            time.sleep(2.0/1000.0)

            t3.start()
            time.sleep(2.0/1000.0)

            t4.start()
            time.sleep(2.0/1000.0)

    def counter_clockwise(self, duration):
        """Rotates the motor counter clockwise

        :param duration: time interval to spin the motor.

        TODO(kvijay1995): Needs to be tested.

        """
        start = time.time()

        while time.time() - start < duration:
            t4.start()
            time.sleep(2.0/1000.0)

            t3.start()
            time.sleep(2.0/1000.0)
            
            t2.start()
            time.sleep(2.0/1000.0)

            t1.start()
            time.sleep(2.0/1000.0)

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

    def rotate_90_counter_clockwise(self):
        """Rotates the motor 90 degrees in the
        counter_clockwise direction.

        """

    @lib.api_call
    def test(self):
        """Test function for the motor."""
        clockwise(15)
