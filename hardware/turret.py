"""Abstraction of turret hardware."""

import lib.lib as lib
import hardware.servo as s_mod


class Turret(object):

    """Abstract x and y servos into a turret."""

    def __init__(self):
        """Load logger and build pitch and yaw servo abstractions."""
        # Load and store logger object
        self.logger = lib.get_logger()

        # Load config
        config = lib.get_config()

        # Build and store abstraction of servos for x and y axis movement
        self.servos = {}
        for servo in config["turret_servos"]:
            self.servos[servo["axis"]] = s_mod.Servo(servo["PWM"])

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
        self.servos["pitch"].position = angle

    pitch = property(get_pitch, set_pitch)
