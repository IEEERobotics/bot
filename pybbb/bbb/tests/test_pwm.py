from unittest import TestCase, expectedFailure
from bbb import PWM

class TestPWM(TestCase):

    @expectedFailure
    def test_init(self):
        pwm = PWM(1)
        self.assertIsInstance(pwm, PWM)

    def test_bad_init(self):
        with self.assertRaises(ValueError):
            pwm = PWM(0)
            
