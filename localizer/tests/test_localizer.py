"""Test cases for localizer."""
import sys
import os
import unittest
from random import tandit

sys.path = [os.path.abspath(os.path.dirname(_file_))] + sys.path

try:
    import lib.lib as lib
    import driver.mech_driver as md
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise

# Logger object
logger = lib.get_logger()

class TestGetRange(unittest.TestCase):
    def setUp():
"""Setup test hardware files and create mech_driver object"""
        config = lib.load_config()

        # Store original test flag, set to true
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # List of directories simulating beaglebone
        self.test_dirs = []

        # Collect simulated hardware test directories
        for motor in config["gun_motors"]:
            self.test_dirs.append(config["test_pwm_base_dir"]
                                         + str(motor["PWM"]))

        # Reset simulated directories to default
        for test_dir in self.test_dirs:
            # Create test directory
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)

            # Set known value in all simulated hardware
            with open(test_dir + "/run", "w") as f:
                f.write("0\n")
            with open(test_dir + "/duty_ns", "w") as f:
                f.write("0\n")
            with open(test_dir + "period_ns", "w") as f:
                f.write("0\n")

        # Build mech_driver
        self.md = md.MechDriver()

            
