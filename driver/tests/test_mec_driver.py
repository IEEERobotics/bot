"""Test cases for mec driver."""
import sys
import os
import unittest
from math import fabs

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import driver.mec_driver as md_mod
    from driver.mec_driver import MecDriver  # for convenience
except ImportError:
    print "ImportError: Use 'python -m unittest discover' from project root."
    raise

# Logger object
logger = lib.get_logger()


class TestRotate(unittest.TestCase):
    """Test rotation of mec wheels"""
    
    def setUp(self):
        """Setup test hardware files and create mec_driver object"""
        config = lib.load_config()

        # Store original test flag, set to true
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # List of directories simulating beaglebone
        self.test_dirs = []

        # Collect simulated hardware test directories
        for motor in config["drive_motors"]:
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
                f.write("250000\n")
            with open(test_dir + "/period_ns", "w") as f:
                f.write("1000000\n")
            with open(test_dir + "/polarity", "w") as f:
                f.write("0\n")

        # Build mec_driver
        self.md = MecDriver()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_rotate(self):
        rotate_speed_error_margin = (MecDriver.max_rotate_speed - MecDriver.min_rotate_speed) * 0.05
        for test_rotate_speed in xrange(MecDriver.min_rotate_speed, MecDriver.max_rotate_speed + 1):
          # Issue rotate command
          logger.debug("Set rotate_speed: {}".format(test_rotate_speed))
          self.md.rotate(test_rotate_speed)
          logger.debug("Check rotate_speed: {}".format(self.md.rotate_speed))
          
          # Check for approximate match, as float values will seldom be exact
          assert fabs(self.md.rotate_speed - test_rotate_speed) < rotate_speed_error_margin
          if fabs(test_rotate_speed) >= 10:   # no point testing direction if speed is too low
              assert self.md.motors["front_left"].direction  == "forward" if test_rotate_speed >= 0 else "reverse"
              assert self.md.motors["front_right"].direction == "reverse" if test_rotate_speed >= 0 else "forward"
              assert self.md.motors["back_left"].direction   == "forward" if test_rotate_speed >= 0 else "reverse"
              assert self.md.motors["back_right"].direction  == "reverse" if test_rotate_speed >= 0 else "forward"
          
          # Check for valid duty cycles (speeds)
          for motor in self.md.motors.itervalues():
              assert MecDriver.min_speed <= motor.speed <= MecDriver.max_speed

    def test_move(self):
        speed_error_margin = (MecDriver.max_speed - MecDriver.min_speed) * 0.05
        angle_error_margin = (MecDriver.max_angle - MecDriver.min_angle) * 0.05
        for test_speed in xrange(MecDriver.min_speed, MecDriver.max_speed + 1, 10):
            for test_angle in xrange(MecDriver.min_angle, MecDriver.max_angle + 1, 10):
                # Issue move command
                logger.debug("Set speed: {}, angle: {}".format(test_speed, test_angle))
                self.md.move(test_speed, test_angle)
                logger.debug("Check speed: {}, angle: {}".format(self.md.speed, self.md.angle))
                
                # Check for approximate match, as float values will seldom be exact
                assert fabs(self.md.speed - test_speed) < speed_error_margin
                if fabs(test_speed) >= 10:  # no point testing angle if speed is too low
                    assert fabs(self.md.angle - test_angle) % 360 < angle_error_margin
                
                # Check for valid duty cycles (speeds)
                for motor in self.md.motors.itervalues():
                    assert MecDriver.min_speed <= motor.speed <= MecDriver.max_speed
