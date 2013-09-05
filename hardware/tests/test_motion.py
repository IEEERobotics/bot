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
        self.drive_motors = [None] * 2
        self.drive_motors[0] = m_mod.Motor(0, 117)  # TODO get from config file
        self.drive_motors[1] = m_mod.Motor(1, 115)  # TODO get from config file
        
        # Set initial speeds to zero
        self.stop()
    
    def tearDown(self):
        # Set speeds back to zero
        self.stop()
    
    def test_forward(self):
        self.drive_motors[0].direction = 1
        self.drive_motors[1].direction = 1
        self.drive_motors[0].speed = 50
        self.drive_motors[1].speed = 50
        time.sleep(2)
        self.stop()
    
    def test_backward(self):
        self.drive_motors[0].direction = 0
        self.drive_motors[1].direction = 0
        self.drive_motors[0].speed = 50
        self.drive_motors[1].speed = 50
        time.sleep(2)
        self.stop()
    
    def test_forward_backward(self):
        self.test_forward()
        self.test_backward()
    
    def test_twist(self):
        # Turn one way
        self.drive_motors[0].direction = 0
        self.drive_motors[1].direction = 1
        self.drive_motors[0].speed = 50
        self.drive_motors[1].speed = 50
        time.sleep(1)
        self.stop()
        
        # Turn the other way
        self.drive_motors[0].direction = 1
        self.drive_motors[1].direction = 0
        self.drive_motors[0].speed = 50
        self.drive_motors[1].speed = 50
        time.sleep(1)
        self.stop()
    
    def test_dance(self):
        """Twist a few times."""
        for i in xrange(5):
            self.test_twist()
    
    def stop(self):
        for motor in self.drive_motors:
            if motor is None: continue
            motor.speed = 0
