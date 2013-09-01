"""
Interpret sensors to derive bot's location.

Note that this is meant to be simple localization, preferably
as computationally light and easy to understand as possible.
The required level of detail is to be able to say which of the
set of discrete block positions the block is located in.

Tentative:
    There will be four ultrasonic sensors facing outwardly in the four
    cardinal directions on the bot.

    These four sensors can uniquely identify the robtos proximity to a
    possible shooting block as long as these requirements are fulfilled.

        1 - The robot knows which of the two straight shooting lines it is on

range = high level time * velocity (340M/S) / 2; we suggest to use over 60ms
measurement cycle, in order to avoid detecting a previous ping

Will I need some way to use standard deviation to pull 'bad' measurements
out of the list of 'pinged' distances when localizing?

Most likely, localization will spur a call to the gunner to look
up an orientation mapped to the discrete set of possible
shooting positions
"""

import lib.lib as lib

#globals might be a bad idea.
MAX_RANGE = 4
MIN_RANGE = .04

#This assumes we will be getting back a positionally defined array
(FRONT, BACK, LEFT, RIGHT) = range(4)


class Localizer(object):

    def __init__(self):
        """Setup and store a global logger,if not already in memory."""
        self.logger = lib.get_logger()

    def which_block(self, distList):
        """Determine the discrete location of the block we're sitting on.

        :returns: The position of the block we're sitting on.

        """

        for dist in distList:
            if dist > MAX_RANGE or dist < MIN_RANGE:
                self.logger.warn('%s is not within the sensors 
                    advertised range', dist
                )

        return {"row": 0, "slot": 0}



    def getPos(self):
        return 1
