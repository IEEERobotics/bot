"""Test case for pid"""

import sys
import os
import unittest

import bot.lib.lib as lib
import tests.test_bot as test_bot
import bot.follower.pid as pid_mod

# Build logger
logger = lib.get_logger()


class TestPID(test_bot.TestBot):

    """Test PID."""

    def setUp(self):
        """Get config and built IR object."""
        super(TestPID, self).setUp()

        # Build PID object
        self.pid = pid_mod.PID()

    def tearDown(self):
        """Restore testing flag state in config file."""
        super(TestPID, self).tearDown()

    def test_pid_kp(self):
        """Test the funtionaty of pid"""
        self.pid.set_k_values(1, 0, 0)
        test_inputs = [0, 0, 0, 1, 2, 3, 4,
                       5, 6, 0, 0, 1, 2, 3, 4, 5, 6, 7]
        print "Run pid kp test"
        for x in test_inputs:
            test_output = self.pid.pid(0, x, 1)
            assert test_output == -x, "{} != {}".format(test_output, x)

    def test_pid_kd(self):
        """Test the funtionaty of pid"""
        difftime = 1.0
        self.pid.set_k_values(0.0, 1.0, 0.0)
        test_inputs = [0.0, 1.0, 2.0, 3.0, 4.0,
                       5.0, 5.0, 5.0, 4.0, 3.0,
                       2.0, 1.0, 0.0, -1.0, -2.0,
                       -6.0, 0.0, -20.0, 0.0]
        test_output = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        output_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        print "Run pid kd test"
        for input_value, index in zip(test_inputs, range(0, len(test_inputs))):
            if index == 0:
                output_value[index] = 0.0
            else:
                output_value[index] = -1 * (
                    test_inputs[index] - test_inputs[index - 1]) / \
                    difftime
        for x, index in zip(test_inputs, range(0, len(test_inputs))):
            test_output[index] = self.pid.pid(0, test_inputs[index], difftime)
            assert abs(test_output[index] - output_value[index]) <= \
                .001, "{} != {}, {}".format(
                    test_output[index], output_value[index], n)
                    
