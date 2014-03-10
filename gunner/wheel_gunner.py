"""Logic for firing using a wheel-based design."""

import time

import gunner
import hardware.wheel_gun as wgun_mod
import lib.lib as lib

class WheelGunner(gunner.Gunner):

    """Specialize gunner to add wheel-based firing logic."""

    def __init__(self):
        """Run superclass's init to build Turret, build WheelGun."""
        super(WheelGunner, self).__init__()

        # Build WheelGun
        self.gun = wgun_mod.WheelGun()

    @lib.api_call
    def fire(self, x_pos, y_pos):
        """Get location, aim turret, accelerate wheels and advance dart."""
        # Go ahead and spin up the gun, to get it to speed
        self.gun.spin = 1

        pitch = self.calc_pitch(x_pos, y_pos)
        yaw = self.calc_yaw(x_pos, y_pos)
        self.aim_turret(yaw, pitch)

        # Wait for turrent to have moved
        time.sleep(.2)

        # Actuate motor to push dart into spinning wheels
        self.gun.fire()
        self.logger.info("Fired dart")
