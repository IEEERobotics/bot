"""Abstraction layer for servos."""

import pybbb.bbb.pwm as pwm_mod

import lib.lib as lib


class Servo(object):

    """Class for abstracting servo settings."""

    def __init__(self, num):
        """Setup logger and PWM interface.

        :param num: ID number of this servo. Also defines PWM number.
        :type num: int
        :param testing: If True, use test HW dir given by config, else real HW.
        :type testing: boolean

        """
        # Get and store logger object
        self.logger = lib.get_logger()

        # Store ID number of servo
        self.num = num

        # Load config
        config = lib.load_config()

        if config["testing"]:
            self.logger.debug("TEST MODE: Servo {}".format(self.num))

            # Get dir of simulated hardware files from config
            test_dir = lib.prepend_prefix(config["test_pwm_base_dir"])
            self.logger.debug("Test HW base dir: {}".format(test_dir))

            # Build PWM object for BBB interaction, provide test dir
            self.pwm = pwm_mod.PWM(self.num, test_dir)
            self.logger.debug("Built {}".format(self.pwm))
        else:
            self.logger.debug("EMBEDDED MODE: Servo {}".format(self.num))

            # Build PWM object for BBB interaction
            self.pwm = pwm_mod.PWM(self.num)
            self.logger.debug("Built {}".format(self.pwm))

        # Set servo to use a 20000ns period TODO(dfarrell07): Confirm this
        self.pwm.period = 20000

        # Set servo to middle position
        self.pwm.duty = 1500
        self.logger.debug("Setup {}".format(self))

    def __str__(self):
        """Override string representation of this object for readability.

        :returns: Human readable representation of this object.

        """
        return "Servo #{}: pos:{} duty/period: {}/{} pol:{}".format(self.num,
                                                             self.position,
                                                             self.pwm.duty,
                                                             self.pwm.period,
                                                             self.pwm.polarity)

    @property
    def position(self):
        """Getter for servo's position as an angle.

        position = ((duty - 1000) / 1000) * 180 where 1000 <= duty <= 2000

        TODO(dfarrell07): This needs to be calibrated.

        :returns: Position of servo as an angle 0-180.

        """
        return int(round(((self.pwm.duty - 1000) / 1000.) * 180))

    @position.setter
    def position(self, position):
        """Setter for servo's position as an angle.

        duty = 1000 + 1000 * (position / 180)

        TODO(dfarrell07): This needs to be calibrated.

        :param position: Position to move the servo to (0-180 degrees).
        :type position: int

        """
        if position > 180:
            self.logger.warn("Invalid pos {}, using 180.".format(position))
            position = 180
        elif position < 0:
            self.logger.warn("Invalid position {}, using 0.".format(position))
            position = 0

        # Set duty
        self.pwm.duty = int(round(1000 + 1000 * (position / 180.)))
        self.logger.debug("Updated {}".format(self))
