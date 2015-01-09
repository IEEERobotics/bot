"""Abstraction layer for stepper motors."""


import bot.lib.lib as lib
import time
import bbb.gpio as gpio
import threading

class Stepper_motor(object):

    """Class for abstracting stepper motor settings."""

    def __init__(self, gpio_1, gpio_2, gpio_3, gpio_4):
        """Setup GPIO interface."""

        # Build logger
        self.logger = lib.get_logger()

        # Load config
        self.config = lib.get_config()

        # This variable is inversely proportional to the speed
        # of rotation. It is set to max speed by default.
        self.time_int = 1.0

        if self.config["test_mode"]["stepper"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir = self.config['test_gpio_base_dir']

            # Build gpio objects for BBB interaction, provide test dir
            self.gpio_1 = gpio.GPIO(gpio_1, gpio_test_dir)
            self.gpio_2 = gpio.GPIO(gpio_2, gpio_test_dir)
            self.gpio_3 = gpio.GPIO(gpio_3, gpio_test_dir)
            self.gpio_4 = gpio.GPIO(gpio_4, gpio_test_dir)

        else:
            # Build gpio pins
            self.gpio_1 = gpio.GPIO(gpio_1)
            self.gpio_2 = gpio.GPIO(gpio_2)
            self.gpio_3 = gpio.GPIO(gpio_3)
            self.gpio_4 = gpio.GPIO(gpio_4)

    def clockwise(self): 
        """The motor rotates clockwise.

        """
        self.gpio_1.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_1.set_value(1)
        self.gpio_2.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_3.set_value(1)
        self.gpio_4.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_4.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_4.set_value(1)
        time.sleep(self.time_int/10000.0)

        self.gpio_1.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(1)
        time.sleep(self.time_int/10000.0)

        self.gpio_1.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_4.set_value(1)
        time.sleep(self.time_int/10000.0)

    def counter_clockwise(self): 
        """Rotates the motor counter clockwise

        """
        self.gpio_4.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_4.set_value(1)
        self.gpio_3.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(1)
        self.gpio_2.set_value(1)
        self.gpio_1.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_1.set_value(0)
        time.sleep(self.time_int/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(1)
        self.gpio_1.set_value(1)
        time.sleep(self.time_int/10000.0)

        self.gpio_4.set_value(0)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(1)
        time.sleep(self.time_int/10000.0)

        self.gpio_4.set_value(1)
        self.gpio_3.set_value(0)
        self.gpio_2.set_value(0)
        self.gpio_1.set_value(1)
        time.sleep(self.time_int/10000.0)

    @property
    def speed(self):
        """Getter for motor's current speed.

        :returns: Speed of the motor.

        """
        return int(round(10000. - self.time_int)/100.)

    @speed.setter
    def speed(self, speed):
        """Setter for the motor's speed.

        :param speed: Speed of motor rotation.
        :type speed: int

        """
        if speed > 100:
            self.logger.warning("Invalid speed {}, using 100%".format(speed))
            speed = 100
        elif speed < 0:
            self.logger.warning("Invalid speed{}, using 0%".format(speed))
            speed = 0

        # Set time interval
        self.time_int = 10001.0-(speed*100.)

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
        """Test function for the motor. Makes the
        motor rotate clockwise until a
        Keyboard interrupt. """
        #try:
        #    while True:
        #        self.clockwise()
        #except KeyboardInterrupt:
        #    print "Done."
        self.rotate_90_clockwise()
