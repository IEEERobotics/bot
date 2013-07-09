#!/usr/bin/env python
"""Logic for firing using a wheel-based design."""

import lib.lib as lib
import gunner
import localizer.localizer as localizer


class WheelGunner(gunner.Gunner):

    """Specialize gunner to add wheel-based firing logic."""

    def __init__(self):
        """Build and store logger."""
        super(WheelGunner, self).__init__()

        #self.logger = lib.get_logger()
        #self.logger.debug("WheelGunner has logger")

        self.localizer = localizer.Localizer()
        self.logger.debug("Gunner has localizer")

    def basic_fire(self):
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

    def update_rotate_speed(self, rotate_speed=100):
        """Accept and handle updates to wheel rotation speed.

        TODO(dfarrell07): This is a stub.

        :param rotate_speed: Desired speed of wheel rotation (% of max).
        :type rotate_speed: float

        """
        self.logger.debug("New rotate speed: {}".format(rotate_speed))

    def advance_dart(self):
        """Cause hardware to push a dart into the spinning wheels.

        TODO(dfarrell07): This is a stub.

        """
        self.logger.debug("Advancing dart")
