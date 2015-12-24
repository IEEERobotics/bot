"""Controls activity related to RGB color sensor."""

import time

import bbb.gpio as gpio_mod
import bot.lib.lib as lib


class Switch():

    """Abstraction for the slider switch"""
    def __init__(self):
        self.logger = lib.get_logger()
        self.bot_config = lib.get_config()

        # Handle off-bone runs
        self.testing = self.bot_config["test_mode"]["slider_switch"]
        if not self.testing:
            self.logger.info("Running in non-test mode")

            # Setup ready signal GPIO:
            self.left_gpio = self.bot_config["slider_switch"]["left_gpio"]
            self.right_gpio = self.bot_config["slider_switch"]["right_gpio"]
            self.left_course_gpio = gpio_mod.GPIO(self.left_gpio)
            self.right_course_gpio = gpio_mod.GPIO(self.right_gpio)
            self.left_course_gpio.input()
            self.right_course_gpio.input()

        else:
            self.logger.info("Running in test mode")

    @lib.api_call
    def detect_switch_orientation(self):
        """Detect which way the slide switch is oriented
        """
        if self.left_course_gpio.get_value():
            return 1
        elif self.right_course_gpio.get_value():
            return 2
        else:
            return 0
