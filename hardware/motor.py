"""Abstraction layer for motors."""

import pybbb.bbb.pwm as pwm_mod

import lib.lib as lib


class Motor(object):
    """Class for abstracting motor settings."""

    def __init__(self, num, testing=False):
        """Setup logger and PWM interface.

        :param num: ID number of this motor. Also defines PWM number.
        :type num: int
        :param testing: If True, use test hw dir given by config, else real hw.
        :type testing: boolean

        """
        # Get and store logger object
        self.logger = lib.get_logger()

        # Store ID number of motor
        self.num = num

        if testing:
            self.logger.debug("TEST MODE: Motor {}".format(num))

            # Load system configuration
            config = lib.load_config()

            # Get dir of simulated hardware files from config
            test_dir = lib.prepend_prefix(config["test_pwm_base_dir"])
            self.logger.debug("Test HW base dir: {}".format(test_dir))

            # Build PWM object for BBB interaction, provide test dir
            self.pwm = pwm_mod.PWM(num, test_dir)
            self.logger.debug("Built {}".format(str(self.pwm)))
        else:
            self.logger.debug("EMBEDDED MODE: Motor {}".format(num))

            # Build PWM object for BBB interaction
            self.pwm = pwm_mod.PWM(num)
            self.logger.debug("Built {}".format(str(self.pwm)))

    @property
    def speed(self):
        """Getter for motor's speed as % of max (same as duty cycle)."""
        return int((self.pwm.duty / float(self.pwm.period)) * 100)

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

        self.pwm.duty = int((speed / 100.) * self.pwm.period)
        self.logger.debug("Set motor {} speed to {}".format(self.num, speed))

    @property
    def direction(self):
        """Getter for motor's direction (same as polarity)."""
        return self.pwm.polarity

    @direction.setter
    def direction(self, direction):
        """Setter for motor's direction (same as polarity).

        :param direction: Direction to rotate motors (1=forward, 0=reverse).
        :type direction: int

        """
        if direction == "forward":
            direction = 1
        elif direction == "reverse":
            direction = 0
        elif direction != 0 and direction != 1:
            self.logger.warn("Invalid dir {}, no update.".format(direction))
            return

        self.pwm.polarity = direction
        self.logger.debug("Set motor {} direction to {}".format(self.num,
                                                                direction))
