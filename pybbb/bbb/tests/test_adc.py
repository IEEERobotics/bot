from unittest import TestCase, expectedFailure
from bbb import ADC

class TestADC(TestCase):

    def test_init(self):
        adc = ADC(0)
        adc = ADC(0, repeat=3)

    @expectedFailure
    def test_init_with_source(self):
        # can't test without mocking the filesystem due to glob
        adc = ADC(0, source='ocp')

    def test_bad_init(self):
        with self.assertRaises(ValueError):
            adc = ADC(7)
        with self.assertRaises(ValueError):
            adc = ADC(-1)
        with self.assertRaises(ValueError):
            adc = ADC(0, source='foo')
            
