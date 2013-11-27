"""Determine which discrete firing block the bot is on using ultrasonics."""

import lib.lib as lib
import localizer
import hardware.us_hub as us_hub_mod


class USLocalizer(localizer.Localizer):

    """Determine which discrete firing block the bot is on using ultrasonics"""

    # From SR04 documentation
    MAX_RANGE = 4
    MIN_RANGE = .04

    # Differences between expected and found values shouldn't exceed this
    MAX_ERROR = 2 * .0254

    def __init__(self):
        """Call parent's __init__, build ultrasonic hub."""
        super(USLocalizer, self).__init__()
        self.us_hub = us_hub_mod.USHub()
        self.block_location = { 'row': -1, 'slot': -1 }

    def update(self):
        """Gather data from sensors and estimate position."""
        us_readings = self.us_hub.read_all()
        for name in self.us_hub.sensors:
            pass  # TODO: Compute position

    def which_block(self):
        """Use ultrasonic sensors to find the block we're over.

        Note: This is a stub.

        :returns: Dict with row and slot of block we're over.

        """
        return self.block_location
