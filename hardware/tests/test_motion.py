"""Test cases for physical bot motion using motors."""
import sys
import os
import unittest
import time

try:
    import lib.lib as lib
    import hardware.motor as m_mod
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()

class TestMotion(unittest.TestCase):
    """Test different motion patterns."""

    def setUp(self):
        """Create motor objects and set initial state to 0 speed."""
        # NOTE Not setting testing flag to True here since we are using physical motors
        
        # Load config
        self.config = lib.load_config()
        
        # Create motor objects to test
        self.num_motors = 4
        self.drive_motors = [None] * self.num_motors
        for i in xrange(self.num_motors):
            self.drive_motors[i] = m_mod.Motor(self.config['drive_motors'][i]['PWM'], self.config['drive_motors'][i]['GPIO'])
        
        # NOTE: 0 = front_right, 1 = front_left, 2 = back_left, 3 = back_right
        
        # Set initial speeds to zero
        self.stop()
    
    def tearDown(self):
        # Set speeds back to zero
        self.stop()
    
    def test_forward(self):
        self.move([1, 1, 0, 0], [50, 50, 50, 50])
        time.sleep(2)
        self.stop()
    
    def test_backward(self):
        self.move([0, 0, 1, 1], [50, 50, 50, 50])
        time.sleep(2)
        self.stop()
    
    def test_forward_backward(self):
        self.test_forward()
        self.test_backward()
    
    def test_strafe(self, dir=0):
        self.move([dir, 1 - dir, 1 - dir, dir], [50, 50, 50, 50])
        time.sleep(1)
        self.stop()
    
    def test_dance(self):
        """Twist a few times."""
        for i in xrange(5):
            self.test_strafe(0)
            self.test_strafe(1)
    
    def move(self, dirs, speeds):
        # NOTE: dirs and speeds must be the same length as self.drive_motors
        for motor, dir, speed in zip(self.drive_motors, dirs, speeds):
            if motor is None: continue
            motor.direction = dir
            motor.speed = speed

    def stop(self):
        for motor in self.drive_motors:
            if motor is None: continue
            motor.speed = 0
