

import sys
from time import time


class PID(object):

    def __init__(self):
        """initizes value for the PID"""
        self.kd = 0
        self.ki = 0
        self.kp = 1
        self.previous_error = 0
        self.integral_error = 0

    def set_k_values(self, kp, kd, ki):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def pid(self, target, process_var, timestep):
        current_error = (target - process_var)
        p_error = self.kp * current_error
        d_error = self.kd * (current_error - self.previous_error) \
            / timestep
        self.integral_error = (
            current_error + self.previous_error) / 2 \
            + self.integral_error
        i_error = self.ki * self.integral_error
        total_error = p_error + d_error + i_error
        self.previous_error = current_error
        return total_error
