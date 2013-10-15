"""Logic for line following."""

import sys

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod
import lib.exceptions as ex


class Follower(object):

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build and store logger.
           Build ir arrays.
           Build motors"""
        self.logger = lib.get_logger()
        self.irs = ir_hub_mod.IRHub()
        self.driver = mec_driver_mod.MecDriver()
        
    def follow(self, state_table):
        """Accept and handle fire commands. """


        current_ir_reading = self.irs.read_all_arrays()
        front_ir = current_ir_reading["front"]
        back_ir = current_ir_reading["back"]
        left_ir = current_ir_reading["left"]
        right_ir = current_ir_reading["right"]
        #self.always_work(cmd)


    def center_cal(self, front, back):
        """ calculate the angle off the line """

        print('hello')
