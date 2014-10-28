#!/usr/bin/env python

import sys
import os
import time
from bbb import GPIO, ADC

adc_num = 6

def time_it(func, n=100):
    t0 = time.time()
    for i in range(n):
        func()
    elapsed = time.time() - t0
    each = elapsed/n
    print " --> {:0.4f} sec total ({:0.3f} ms/read, {:d} Hz)".format(
            elapsed, 1000 * each, int(1/each))
    print

print "Reading GPIO via /sys interface..."
gpio = GPIO(2)
time_it(gpio.get_value)

print "Reading ADCs (no repeat) via IIO sysfs interface..."
adc = ADC(adc_num, source='iio', repeat=1)
time_it(adc.raw)

print "Reading voltage (repeat=8) via IIO sysfs interface..."
adc = ADC(adc_num, source='iio')
time_it(lambda: adc.volts)

print "Reading GPIO via /sys interface..."
gpio = GPIO(2)
time_it(gpio.get_value, n=1000)

