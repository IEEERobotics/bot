"""Abstraction of turret hardware."""

import bot.lib.lib as lib
import bot.hardware.servo as s_mod


class Turret(object):

    """Abstract x and y servos into a turret."""

    def __init__(self):
        """Load logger and build pitch and yaw servo abstractions."""
        # Load and store logger object
        self.logger = lib.get_logger()

        # Load config
        config = lib.get_config()
        self.config = config['turret']

        # Build and store abstraction of servos for x and y axis movement
        self.servos = {}
        for servo, conf in self.config['servos'].items():
            self.servos[servo] = s_mod.Servo(conf['PWM'])

    def __str__(self):
        """Represent turret in a human-readable way."""
        return "Turret: yaw:{}, pitch:{}".format(self.servos["yaw"],
                                                 self.servos["pitch"])

    @lib.api_call
    def get_yaw(self):
        """Getter for position in degrees of turret on x-axis.

        :returns: Angle in degrees of turret on x-axis.

        """
        return self.servos["yaw"].position

    @lib.api_call
    def set_yaw(self, angle):
        """Setter for position of turret on yaw-axis.

        :param angle: Angle in degrees to set turret to on yaw-axis.

        """
        # TODO: move min/max clampig logic to Servo class
        axis_min = self.config['servos']['yaw']['min']
        axis_max = self.config['servos']['yaw']['max']
        if not (axis_min <= angle <= axis_max):
            self.logger.warning(
                "Clamping yaw angle to bounds {} => [{},{}]".format(
                    angle, axis_min, axis_max))
            angle = max(axis_min, min(axis_max, angle))
        self.servos["yaw"].position = angle

    yaw = property(get_yaw, set_yaw)

    @lib.api_call
    def get_pitch(self):
        """Getter for position in degrees of turret on pitch-axis.

        :returns: Angle in degrees of turret on pitch-axis.

        """
        return self.servos["pitch"].position

    @lib.api_call
    def set_pitch(self, angle):
        """Setter for position of turret on pitch-axis.

        :param angle: Angle in degrees to set turret to on pitch-axis.

        """
        axis_min = self.config['servos']['pitch']['min']
        axis_max = self.config['servos']['pitch']['max']
        if not (axis_min <= angle <= axis_max):
            self.logger.warning(
                "Clamping pitch angle to bounds {} => [{},{}]".format(
                    angle, axis_min, axis_max))
            angle = max(axis_min, min(axis_max, angle))
        self.servos["pitch"].position = angle

    @lib.api_call
    def aim(self, pitch, yaw):
        """Thin wrapper for setting pitch and yaw in one command.

        :param pitch: Angle in degees to set turn to on pitch axis.
        :type pitch: float
        :param yaw: Angle in degees to set turn to on pitch axis.
        :type yaw: float

        """
        self.set_pitch(pitch)
        self.set_yaw(yaw)

    pitch = property(get_pitch, set_pitch)
