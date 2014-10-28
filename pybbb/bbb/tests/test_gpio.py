from unittest import TestCase, expectedFailure
from bbb import GPIO

class TestGPIO(TestCase):

    @expectedFailure
    def test_init(self):
        pwm = GPIO(1)
        self.assertIsInstance(pwm, GPIO)

    def test_bad_init(self):
        with self.assertRaises(ValueError):
            pwm = GPIO(0)
            
