#!/usr/bin/env python
"""Logic for firing using a wheel-based design."""

from time import sleep

import lib.lib as lib
import gunner
import hardware.motor as motor
import hardware.solenoid as solenoid


class WheelGunner(gunner.Gunner):

    """Specialize gunner to add wheel-based firing logic."""

    def __init__(self):
        """Run superclass's init."""
        super(WheelGunner, self).__init__()

        # Build solenoid for advancing dart
        self.dart_sol = solenoid.Solenoid(0)

        # Build motors for driving wheels
        self.motors = []
        self.motors.append(motor.Motor(0))
        self.motors.append(motor.Motor(1))

    def fire(self, cmd):
        """Handle normal fire commands.

        TODO(dfarrell07): This is a stub

        """
        # Get the block we're over
        block = self.localizer.which_block()
        self.logger.debug("Loc: {}".format(block))

        # Aim turret and fire dart
        self.aim_turret()
        self.update_rotate_speed()
        self.advance_dart()
        self.logger.info("Fired dart")

    @property
    def wheel_speed(self):
        """Getter for wheel rotation speed. Speed is % of max."""
        assert self.motors[0].speed == self.motors[1].speed, "{} != {}".format(
            self.motors[0].speed, self.motors[1].speed)
        return self.motors[0].speed

    @wheel_speed.setter
    def wheel_speed(self, speed=100):
        """Setter for updates to wheel rotation speed.

        :param speed: Desired speed of wheel rotation (% of max).
        :type speed: int

        """
        for motor in self.motors:
            motor.speed = speed
        self.logger.debug("New wheel speed: {}".format(speed))

    def advance_dart(self):
        """Cause hardware to push a dart into the spinning wheels.

        TODO(dfarrell07): This is a stub.

        """
        self.logger.debug("Advancing dart")
        self.dart_sol.extend()
        sleep(.5)
        self.dart_sol.retract()
