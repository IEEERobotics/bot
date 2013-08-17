"""Abstraction layer for motors."""

import pybbb.bbb.pwm as pwm_mod

import lib.lib as lib

FORWARD = 1
REVERSE = 0


class Motor(object):
    """Class for abstracting motor settings."""

    def __init__(self, num):
        """Setup logger and PWM interface.

        :param num: ID number of this motor. Also defines PWM number.
        :type num: int
        :param testing: If True, use test HW dir given by config, else real HW.
        :type testing: boolean

        """
        # Get and store logger object
        self.logger = lib.get_logger()

        # Store ID number of motor
        self.num = num

        # Load system configuration
        config = lib.load_config()

        if config["testing"]:
            self.logger.debug("TEST MODE: Motor {}".format(self.num))

            # Get dir of simulated hardware files from config
            test_dir = lib.prepend_prefix(config["test_pwm_base_dir"])
            self.logger.debug("Test HW base dir: {}".format(test_dir))

            # Build PWM object for BBB interaction, provide test dir
            self.pwm = pwm_mod.PWM(self.num, test_dir)
            self.logger.debug("Built {}".format(self.pwm))
        else:
            self.logger.debug("EMBEDDED MODE: Motor {}".format(self.num))

            # Build PWM object for BBB interaction
            self.pwm = pwm_mod.PWM(self.num)
            self.logger.debug("Built {}".format(self.pwm))

        # Setup initial speed and direction
        self.speed = 0
        self.direction = FORWARD
        self.logger.debug("Setup {}".format(self))

    def __str__(self):
        """Override string representation of this object for readability.

        :returns: Human readable representation of this object.

        """
        return "Motor #{}: speed:{} direction:{}".format(self.num,
                                                         self.speed,
                                                         self.direction)

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
        """Getter for motor's direction (same as polarity).

        :returns: Direction of motor ("forward" or "reverse").

        """
        if self.pwm.polarity == FORWARD:
            return "forward"
        elif self.pwm.polarity == REVERSE:
            return "reverse"
        else:
            self.logger.error("Invalid polarity: {}".format(self.pwm))

    @direction.setter
    def direction(self, direction):
        """Setter for motor's direction (same as polarity).

        :param direction: Direction to rotate motors (1=forward, 0=reverse).
        :type direction: int

        """
        if direction == "forward":
            direction = FORWARD
        elif direction == "reverse":
            direction = REVERSE
        elif direction != 0 and direction != 1:
            self.logger.warn("Invalid dir {}, no update.".format(direction))
            return

        self.pwm.polarity = direction
        self.logger.debug("Updated direction {}".format(self))
