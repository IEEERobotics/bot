"""A early version of the line follower."""

import hardware.ir_hub as ir_hub_mod
import lib.lib as lib
import driver.mec_driver as driver_mod


class SimpleFollower(object):

    """A early version of the line follower."""

    def __init__(self):
        """Setup driver, logger, ir_hub, and config."""
        self.logger = lib.get_logger()
        self.ir_hub = ir_hub_mod.IRHub()
        self.driver = driver_mod.MecDriver()
        self.config = lib.get_config()

    def overall_move(self):
        """Constant loop for the movement information."""
        while True:
            dic = self.ir_hub.read_all()
            if on_line(dic["front"], dic["back"]):
                rotate_correct()
            else:
                move()

    def move(self, array_dictionary):
        """Receives the dict of IR arrays of returns a (speed, angle) tuple.

        :param array_dictionary: Dicty with 4 IR arrays
        :returns: A speed and angle

        """

        front = array_dictionary()["front"]
        if front == 0:
            # Mid and centered
            return (100, 0)
        elif front == 1:
            # Right and centered
            return (80, 30)
        elif front == 2:
             # Left and centered
            return(80, -30)

    def slope_between(self, point_a, point_b):
        """Determines the slope between two points.

        The measurement should come from the physical bot.

        :point_a: First point of pair of points to find slope between
        :point_b: Second point of pair of points to find slope between

        """
        return (ya - yb) / (xa - xb)

    def weigh_array(self, A, parts):
        """Separates an array into parts and ranks them from high to low.

        :parts: The number of sections the list is to be split into

        """

        for x in range(0, list.max):
            step = len(A) % parts
            which_part = -1
            for x in range(0, parts):
                # For each part of the of the list find the max
                if a == max(A[0:len(A):step], old_max):
                    old_max = a
                # TODO: Invalid and I don't know what you mean, @Kaleb
                #return() # the old max
        return (speed, angle)

    def move_multi(self):
        """Determines the direction to move the bot."""
        half_length = self.config["irs_per_array"] / 2
        mid_space = 2
        front = self.ir_hub.read_all()["front"]

        values = []
        f_left = self.sum_array(front, 0, half_length - mid_space)
        f_right = self.sum_array(front, half_length + mid_space,
                                 self.config["irs_per_array"])
        f_mid = self.sum_array(front, (half_length - mid_space) / 2,
                               (half_length + mid_space) / 2)
        if f_mid > f_left or f_mid > f_right:
            # Go straight
            self.driver.move(100, 0)
            self.logger.debug("IR in mid range: moves forward")
        elif f_left > f_right:
            # Move to the right
            self.driver.move(100, 270)
            self.logger.debug("front left IR > front right: move right")
        else:
            # Move to the left
            self.driver.move(100, 90)
            self.logger.debug("front right IR > front left: move left")

    def sum_array(self, array, start, end):
        """Sums the values in a given range.

        :param array: A list to sum.
        :param start: The starting point to sum from.
        :param end: The ending point to sum to.
        :returns: The sum of the values from start to end.

        """
        val_sum = 0
        for x in range(start, end):
            val_sum += array[x]
        return val_sum
