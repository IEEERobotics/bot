"""
Localizer: A Minimalist Implementation

Requisites:
    - One SR04 Ultrasonic transmitter/receiver pair
    - Two GPIO pins on our microcontroller
    - A guranteed orientation for the robot at firing time
    - Knowledge of which of the three firing lines the bot is on.
          I assume we'll hit them sequentially

This version of localzer will:
    - Determine the bot's distance from the 'right' wall.
    - The measured distance will be checked against a pre-existing list
          of discrete firing point distances for each line.
"""

try:
    import lib.lib as lib
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise

class Localizer(object):

    #From SR04 documentation
    MAX_RANGE = 4
    MIN_RANGE = .04

    #Differences between expected and found values shouldn't exceed this
    MAX_ERROR = 2*.0254

    #Firing position lists for each line.
    #Converting inches to meters
    LINE_1 = [
        7*.0254, 9*.0254, 11*.0254, 13*.0254, 15*.0254, 17*.0254, 19*.0254,
        21*.0254, 23*.0254, 25*.0254, 27*.0254, 29*.0254, 31*.0254
    ]
    #Coming soon
    LINE_2 = []
    #Distance from firing position to the right wall will be the same as first
    LINE_3 = LINE_1

    def __init__(self):
        """
        Setup and store a global logger,if not already in memory.
        """
        self.logger = lib.get_logger()

    def which_block(self, lineList, distance):
        """
        input: One of the three line's list of firing positions
        and a distance to be compared to each item inside it.

        returns: The index of the firing position from the line list that is
        closest to the distance retrieved from the ultrasonic sensor
        """
        if distance > self.MAX_RANGE or distance < self.MIN_RANGE:
            self.logger.warn(
                """%s meters is not within the sensor\'s
                advertised range
                """, distance
            )

        diff = {}
        i = 0
        for item in lineList:
            diff[i] = (abs(item - distance))
            i += 1

        #firingPos will be the index of the closest firing position in the line's list
        firingPos = min(diff, key=diff.get)

        if diff[firingPos] > self.MAX_ERROR:
            self.logger.warn('%s meters is too much error', diff[firingPos])

        return firingPos
