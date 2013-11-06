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
        self.gun_sol = s_mod.Solenoid(self.config["gun_sol"]["GPIO"])

        # Build motors for driving wheels
        self.motors = []
        for motor in self.config["gun_motors"]:
            self.motors.append(m_mod.Motor(motor["PWM"]))

    def auto_fire(self):
        """Get location, aim turret, accelerate wheels and advance dart."""
        # Get the block we're over
        block = self.localizer.which_block()
        self.logger.debug("Location: {}".format(block))

        # Get targeting information for the block we're over
        yaw = self.targ["rows"][block["row"]]["slots"][block["slot"]]["yaw"]
        ptch = self.targ["rows"][block["row"]]["slots"][block["slot"]]["pitch"]
        spd = self.targ["rows"][block["row"]]["slots"][block["slot"]]["speed"]

        # Aim turret and fire dart
        self.aim_turret(yaw, ptch)
        # TODO(dfarrell07): Wait until turret has moved
        self.wheel_speed = spd
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
        try:
            assert 0 <= speed <= 100
        except AssertionError:
            self.logger.error("Speed {} is out of bounds".format(speed))
            raise AssertionError("Speed is out of bounds")

        for motor in self.motors:
            motor.speed = speed
        self.logger.debug("New wheel speed: {}".format(speed))

    def advance_dart(self):
        """Cause hardware to push a dart into the spinning wheels."""
        self.logger.debug("Advancing dart")
        self.gun_sol.extend()
        if not self.config["testing"]:
            sleep(self.config["sol_extend_delay"])
        self.gun_sol.retract()
