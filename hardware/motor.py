"""Abstraction layer for motors."""

import pybbb.bbb.pwm as pwm_mod

import lib.lib as lib


class Motor(object):
    """Class for abstracting motor settings."""

    def __init__(self, num, testing=False):
        """Setup logger and PWM interface.

        :param num: ID number of this motor. Also defines PWM number.
        :type num: int

        """
        # Get and store logger object
        self.logger = lib.get_logger()
        self.logger.debug("Motor {} has logger".format(num))

        # Store ID number of motor
        self.num = num

        if testing:
            self.logger.debug("TEST MODE: Motor {}".format(num))
            config = lib.load_config()

            # Get dir of simulated hardware files from config
            test_base_dir = lib.prepend_prefix(config["test_base_dir"])
            self.logger.debug("Test HW dir: {}".format(test_base_dir))

            # Build PWM object for BBB interaction, provide test dir
            self.pwm = pwm_mod.PWM(num, test_base_dir)
            self.logger.debug("Built {}".format(str(self.pwm)))
        else:
            self.logger.debug("EMBEDDED MODE: Motor {}".format(num))
            # Build PWM object for BBB interaction
            self.pwm = pwm_mod.PWM(num)
            self.logger.debug("Built {}".format(str(self.pwm)))

        # Set motor speed/direction to current value of PWM duty/polarity
        self._speed = self.pwm.duty
        self.logger.debug("Motor {} speed: {}".format(num, self._speed))
        self._direction = self.pwm.polarity
        self.logger.debug("Motor {} direction: {}".format(num,
                                                          self._direction))

    @property
    def speed(self):
        """Getter for motor's speed as % of max (same as duty cycle)."""
        return self.pwm.duty

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

        self.pwm.duty = speed
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
        if direction != 0 and direction != 1:
            self.logger.warn("Invalid dir {}, no update.".format(direction))
            return

        self.pwm.polarity = direction
        self.logger.debug("Set motor {} direction to {}".format(self.num,
                                                                direction))
