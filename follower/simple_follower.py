"""A earlier version of the line follower."""

import hardware.ir_hub as ir_hub_mod
import lib.lib as lib
import driver.mec_driver as driver_mod


class SimpleFollower(object):

    """A earlier version of the line follower."""

    def __init__(self):
        """Setup driver, logger, ir_hub, and config."""
        self.logger = lib.get_logger()
        self.ir_hub = ir_hub_mod.IRHub()
#       self.driver = driver_mod.MecDriver()
        self.config = lib.load_config()

    def move_multi(self):
        """Determines the direction to move the bot."""
        half_length = self.config["irs_per_array"] / 2
        mid_space = 2
        front = self.ir_hub.read_all_arrays()["front"]

        values = []
        f_left = self.sum_array(front, 0, half_length - mid_space)
        f_right = self.sum_array(front, half_length + mid_space,
                                 self.config["irs_per_array"])
        f_mid = self.sum_array(front, (half_length - mid_space) / 2,
                               (half_length + mid_space) / 2)
        if f_mid > f_left or f_mid > f_right:
            # Go straight
            # self.driver.move(100, 0)
            self.logger.debug("IR in mid range: moves forward")
        elif f_left > f_right:
            # Move to the right
            # self.driver.move(speed, angle)
            self.logger.debug("front left IR > front right: move right")
        else:
            # Move to the left
            # self.driver.move(speed, angle)
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
