"""Logic for firing using a wheel-based design."""

from time import sleep

import lib.lib as lib
import gunner
import hardware.wheel_gun as wgun_mod


class WheelGunner(gunner.Gunner):

    """Specialize gunner to add wheel-based firing logic."""

    def __init__(self):
        """Run superclass's init to build Turret, build WheelGun."""
        super(WheelGunner, self).__init__()

        # Build WheelGun
        self.gun = wgun_mod.WheelGun()

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
        # TODO: Update to use variable speed once capes are installed
        self.gun.spin = 1
        self.gun.fire()
        self.logger.info("Fired dart")
