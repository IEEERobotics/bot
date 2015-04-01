"""Encapsulates functionality required to operate the micromotors (polulu)."""

import time
from math import pi

import bot.lib.lib as lib
import bbb.gpio as gpio

class Micromotor(object):

    def __init__(self, gpio_pins):
        """Setup GPIO interface."""

        # Build logger
        self.logger = lib.get_logger()

        # Load config
        self.config = lib.get_config()

        if self.config["test_mode"]["micromotor"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir = self.config['test_gpio_base_dir']

            # Build gpio objects for BBB interaction
            self.gpio_1 = gpio.GPIO(gpio_pins[0], gpio_test_dir)
            self.gpio_2 = gpio.GPIO(gpio_pins[1], gpio_test_dir)

        else:
            # Build gpio pins
            self.gpio_1 = gpio.GPIO(gpio_pins[0])
            self.gpio_2 = gpio.GPIO(gpio_pins[1])

        # init all pins as output
        self.gpio_1.output()
        self.gpio_2.output()

    def forward(self):
        """The motor move clockwise.

        """
        self.gpio_1.set_value(1)

    def stop(self):
        """Stop the motor when it is moving.

        """
        self.gpio_1.set_value(0)
        self.gpio_2.set_value(0)

    def backward(self):
        """The motor moves counter_clockwise.

        """
        self.gpio_2.set_value(1)
