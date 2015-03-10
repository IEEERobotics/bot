"""Abstraction layer for motors."""

import bbb.pwm as pwm_mod
import bbb.gpio as gpio_mod

import bot.lib.lib as lib

FORWARD = 1
REVERSE = 0


class Motor(object):

    """Class for abstracting motor settings.

    Note that motors without GPIO pins are assumed to not need to change
    direction in-code. Their direction should be manually changed by
    switching the wires that drive them.

    """

    def __init__(self, pwm_num, gpio_num=None, inverted=False):
        """Build GPIO and PWM pins, set initial values.

        Note that the default gpio_num=None param implies that the motor
        has no direction. Its direction should be manually changed by
        swapping the wires that drive it.

        :param pwm_num: PWM number for this motor.
        :type pwm_num: int
        :param gpio_num: Optional GPIO number for this motor.
        :type gpio_num: int
        :param inverted: Whether to treat direction as inverted.
        :type inverted: bool

        """
        # Get and store logger object
        self.logger = lib.get_logger()

        # Store PWM and GPIO numbers of motor
        self.pwm_num = pwm_num
        self.gpio_num = gpio_num

        # Set motor-specific forward and reverse values based on inverted
        # TODO: Make this a config flag
        self.invert(inverted)

        # Load system configuration
        config = lib.get_config()

        if config["test_mode"]["motor"]:
            # Get dir of simulated hardware files from config
            pwm_test_dir = config["test_pwm_base_dir"]

            # Build PWM object for BBB interaction, provide test dir
            self.pwm = pwm_mod.PWM(self.pwm_num, pwm_test_dir)

            if self.gpio_num is not None:
                # Build GPIO object for BBB interaction, provide test dir
                gpio_test_dir = config["test_gpio_base_dir"]
                self.gpio = gpio_mod.GPIO(self.gpio_num, gpio_test_dir)
        else:
            # Build PWM object for BBB interaction
            self.pwm = pwm_mod.PWM(self.pwm_num)

            if self.gpio_num is not None:
                # Build GPIO object for BBB interaction
                self.gpio = gpio_mod.GPIO(self.gpio_num)

        # Polarity should be 0 to get X% high at X PWM.
        self.pwm.polarity = 0

        # Setup initial speed and direction
        self.speed = 0
        if self.gpio_num is not None:
            self.direction = FORWARD
        self.logger.debug("Setup {}".format(self))

    def __str__(self):
        """Override string representation of this object for readability.

        :returns: Human readable representation of this object.

        """
        if self.gpio_num is None:
            return "Motor PWM:{} GPIO:None speed:{}".format(
                self.pwm_num, self.speed)
        return "Motor PWM:{} GPIO:{} speed:{} dir:{} vel:{}".format(
            self.pwm_num,
            self.gpio_num,
            self.speed,
            self.direction,
            self.velocity)

    def invert(self, inverted):
        """Provides ability to invert motor direction.

        This is needed to account for the physical position of motors.

        :param inverted: True to swap typical forward and reverse directions.
        :type inverted: bool

        """
        self.inverted = inverted
        if self.inverted:
            self.forward = REVERSE
            self.reverse = FORWARD
        else:
            self.forward = FORWARD
            self.reverse = REVERSE

    def get_speed(self):
        """Getter for motor's speed as % of max (same as duty cycle).

        :returns: Current motor speed as percent of max speed.

        """
        return int(round((self.pwm.duty / float(self.pwm.period)) * 100))

    def set_speed(self, speed):
        """Setter for motor's speed as % of max (same as duty cycle).

        :param speed: Speed to set motor to in % of maximum.
        :type speed: float

        """
        speed = int(round(speed))
        if speed > 100:
            self.logger.warning("Invalid speed {}, using 100".format(speed))
            speed = 100
        elif speed < 0:
            self.logger.warning("Invalid speed {}, using 0".format(speed))
            speed = 0

        self.pwm.duty = int(round((speed / 100.) * self.pwm.period))
        self.logger.debug("Updated speed {}".format(self))

    speed = property(get_speed, set_speed)

    def get_direction(self):
        """Getter for motor's direction.

        Motors that have no GPIO pin have no coded direction. This method
        will return None in that case. Set motor direction by manually
        switching the motor's wires.

        :returns: Direction of motor ("forward", "reverse" or None).

        """
        if self.gpio_num is None:
            self.logger.warning("{} doesn't own a GPIO".format(self))
            return None

        if self.gpio.value == self.forward:
            return "forward"
        elif self.gpio.value == self.reverse:
            return "reverse"
        else:
            self.logger.error("Invalid polarity: {}".format(self.gpio))

    def set_direction(self, direction):
        """Setter for motor's direction. Toggles a GPIO pin.

        Motors that have no GPIO pin have no coded direction. This method
        will return None in that case. Set motor direction by manually
        switching the motor's wires.

        :param direction: Dir to rotate motors (1="forward", 0="reverse").
        :type direction: int or string

        """
        if self.gpio_num is None:
            self.logger.warning("{} doesn't own a GPIO".format(self))
            return None

        if direction == "forward":
            direction = self.forward
        elif direction == "reverse":
            direction = self.reverse
        elif direction != 0 and direction != 1:
            self.logger.warning("Invalid dir {}, no update.".format(direction))
            return

        self.gpio.value = direction
        self.logger.debug("Updated direction {}".format(self))

    direction = property(get_direction, set_direction)

    def get_velocity(self):
        """Getter for motor's velocity as % of max (+ forward, - backward).

        Note that directionless motors (no assigned GPIO pin) will return +.

        :returns: Current motor velocity as % of max with signed direction.

        """
        if self.gpio_num is None:
            return self.speed

        return self.speed * (1 if self.gpio.value == self.forward else -1)

    velocity = property(get_velocity)
