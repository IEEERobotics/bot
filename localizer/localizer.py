"""
Localizer - Determine which discrete firing 'block' the bot is on.

Requisites:
    - Four SR04 Ultrasonic transmitter/receiver pairs
    - Two GPIO pins on our microcontroller per sensor/receiver
    - A guranteed orientation for the robot at firing time
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
    MAX_ERROR = 2 * .0254

    #Firing position lists for each line.
    #Converting inches to meters
    LINE_1 = []
    #Coming soon
    LINE_2 = []
    #Distance from firing position to the right wall will be the same as first
    LINE_3 = LINE_1

    def __init__(self):
        """
        Setup and store a global logger,if not already in memory.
        """
        self.logger = lib.get_logger()

    def which_block(self):
        """
        Returns: A dictionary containing a row and a slot
        """

        """
        if distance > self.MAX_RANGE or distance < self.MIN_RANGE:
            self.logger.warn(
                %s meters is not within the sensor\'s
                advertised range
                , distance
            )

        diff = {}
        i = 0
        for item in lineList:
            diff[i] = (abs(item - distance))
            i += 1

        firingPos = min(diff, key=diff.get)

        if diff[firingPos] > self.MAX_ERROR:
            self.logger.warn('%s meters is too much error', diff[firingPos])
        """

        firingPos = {'row': 0, 'slot': 0}
        return firingPos
