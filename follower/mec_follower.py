"""Logic for following lines using Mecanum wheels."""

import sys
from time import time, sleep

import numpy as np

import lib.lib as lib
import pid ad pid_mod



class MecFollower(object):
    """Subclass of Follower for line-following using mecanum wheels."""

    def __init__(self):
        # Build logging
        self.logger = lib.get_logger()

        # Build subsystems
        self.ir_hub = ir_hub_mod.IRHub()
        self.ir_hub.thrsh = 100
        
        # Build PID class
        self.front_right = pid_mod.PID()
        self.front_left = pid_mod.PID()
        self.back_right = pid_mod.PID()
        self.back_left = pid_mod.PID()
