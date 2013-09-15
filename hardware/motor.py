"""Abstraction layer for motors."""

import pybbb.bbb.pwm as pwm_mod
import pybbb.bbb.gpio as gpio_mod

import lib.lib as lib

FORWARD = 1
REVERSE = 0


class Motor(object):

    """Class for abstracting motor settings."""

    def __init__(self, pwm_num, gpio_num):
        """Setup logger and PWM interface.

        :param pwm_num: PWM number for this motor.
        :type pwm_num: int
        :param gpio_num: GPIO number for this motor.
        :type gpio_num: int

        """
        # Get and store logger object
        self.logger = lib.get_logger()

        # Store PWM and GPIO numbers of motor
        self.pwm_num = pwm_num
        self.gpio_num = gpio_num

        # Load system configuration
        config = lib.load_config()

        if config["testing"]:
            # Get dir of simulated hardware files from config
            pwm_test_dir = lib.prepend_prefix(config["test_pwm_base_dir"])
            gpio_test_dir = lib.prepend_prefix(config["test_gpio_base_dir"])

            # Build PWM object for BBB interaction, provide test dir
            self.pwm = pwm_mod.PWM(self.pwm_num, pwm_test_dir)

            # Build GPIO object for BBB interaction, provide test dir
            self.gpio = gpio_mod.GPIO(self.gpio_num, gpio_test_dir)
        else:
            # Build PWM object for BBB interaction
            self.pwm = pwm_mod.PWM(self.pwm_num)

            # Build GPIO object for BBB interaction
            self.gpio = gpio_mod.GPIO(self.gpio_num)

        # Polarity should be 0 to get X% high at X PWM.
        self.pwm.polarity = 0

        # Setup initial speed and direction
        self.speed = 0
        self.direction = FORWARD
        self.logger.debug("Setup {}".format(self))

    def __str__(self):
        """Override string representation of this object for readability.

        :returns: Human readable representation of this object.

        """
        return "Motor PWM:{} GPIO:{} speed:{} dir:{} vel:{}".format(self.pwm_num,
                                                             self.gpio_num,
                                                             self.speed,
                                                             self.direction,
                                                             self.velocity)

    @property
    def speed(self):
        """Getter for motor's speed as % of max (same as duty cycle).

        :returns: Current motor speed as percent of max speed.

        """
        return int(round((self.pwm.duty / float(self.pwm.period)) * 100))

    @speed.setter
    def speed(self, speed):
        """Setter for motor's speed as % of max (same as duty cycle).

        :param speed: Speed to set motor to in % of maximum.
        :type speed: int

        """
        if speed > 100:
            self.logger.warn("Invalid speed {}, using 100.".format(speed))
            speed = 100
        elif speed < 0:
            self.logger.warn("Invalid speed {}, using 0.".format(speed))
            speed = 0

        self.pwm.duty = int(round((speed / 100.) * self.pwm.period))
        self.logger.debug("Updated speed {}".format(self))

    @property
    def direction(self):
        """Getter for motor's direction.

        :returns: Direction of motor ("forward" or "reverse").

        """
        if self.gpio.value == FORWARD:
            return "forward"
        elif self.gpio.value == REVERSE:
            return "reverse"
        else:
            self.logger.error("Invalid polarity: {}".format(self.gpio))

    @direction.setter
    def direction(self, direction):
        """Setter for motor's direction. Toggles a GPIO pin.

        :param direction: Dir to rotate motors (1="forward", 0="reverse").
        :type direction: int or string

        """
        if direction == "forward":
            direction = FORWARD
        elif direction == "reverse":
            direction = REVERSE
        elif direction != 0 and direction != 1:
            self.logger.warn("Invalid dir {}, no update.".format(direction))
            return

        self.gpio.value = direction
        self.logger.debug("Updated direction {}".format(self))

    @property
    def velocity(self):
        """Getter for motor's velocity as % of max (same as duty cycle), with +ve being forward, -ve backward.

        :returns: Current motor velocity as percent of max, signed based on direction.

        """
        return self.speed * (1 if self.gpio.value == FORWARD else -1)
