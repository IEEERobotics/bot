"""Logic for firing using a wheel-based design."""

from time import sleep

import lib.lib as lib
import gunner
import hardware.motor as m_mod
import hardware.solenoid as s_mod


class WheelGunner(gunner.Gunner):

    """Specialize gunner to add wheel-based firing logic."""

    def __init__(self):
        """Run superclass's init."""
        super(WheelGunner, self).__init__()

        # Build solenoid for advancing dart
        self.dart_sol = s_mod.Solenoid(self.config["dart_solenoid"]["GPIO"])

        # Build motors for driving wheels
        self.motors = []
        for motor in self.config["gun_motors"]:
            self.motors.append(m_mod.Motor(motor["PWM"]))

    def fire(self, cmd):
        """Get location, aim the turret, accelerate wheels and advance dart.

        :param cmd: Description of fire command. Currently just text summary.

        """
        self.logger.debug("{}".format(cmd["summary"]))

        # Get the block we're over
        block = self.localizer.which_block()
        self.logger.debug("Location: {}".format(block))

        # Get targeting information for the block we're over
        x = self.targ["rows"][block["row"]]["slots"][block["slot"]]["x_angle"]
        y = self.targ["rows"][block["row"]]["slots"][block["slot"]]["y_angle"]
        spd = self.targ["rows"][block["row"]]["slots"][block["slot"]]["speed"]

        # Aim turret and fire dart
        self.aim_turret(x, y)
        # TODO(dfarrell07): Wait until turret has moved
        self.wheel_speed = spd
        # TODO(dfarrell07): Confirm speed via encoders
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
        """Cause hardware to push a dart into the spinning wheels."""
        self.logger.debug("Advancing dart")
        self.dart_sol.extend()
        sleep(.5)
        self.dart_sol.retract()
