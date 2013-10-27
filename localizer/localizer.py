"""Determine which discrete firing block the bot is on."""

import lib.lib as lib


class Localizer(object):

    """Determine which discrete firing block the bot is on."""

    def __init__(self):
        """Build logger."""
        # Build and store logger
        self.logger = lib.get_logger()

    def which_block(self):
        """Use ultrasonic sensors to find the block we're over.

        This method is not meant to be called, but instead is meant to show
        that subclasses should override it in their implementation.

        Implementations should return a dict with two key/value pairs.
        One key should be 'row', and should contain the number of the row 
        the bot's over. The other should be 'slot', and should contain 
        the number of the block position on that row the bot's over.

        """
        self.logger.error("Method must be overridden by a subclass.")
        raise NotImplementedError("Subclass must override this method.")
