"""Logic for determining the bot's location."""

import lib.lib as lib


class Localizer(object):

    """Interpret sensors to derive bot's location.

    Note that this is meant to be simple localization, preferably
    as computationally light and easy to understand as possible.
    The required level of detail is to be able to say which of the
    set of discrete block positions the block is located in.

    """

    def __init__(self):
        """Setup and store a global logger,if not already in memory."""
        self.logger = lib.get_logger()

    def which_block(self):
        """Determine the discrete location of the block we're sitting on.

        TODO(dfarrell07): This is a stub

        :returns: The position of the block we're sitting on.

        """
        return {"row": 0, "slot": 0}
