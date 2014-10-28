#!/usr/bin/env python

import sys
import os
import time
from bbb import GPIO

gpio_num = 3
gpio = GPIO(gpio_num)
gpio.output()

print "start value {}: {}".format(gpio, gpio.value)

print "Set {} --> {}".format(gpio, 0)
gpio.set_value(0)
print "Read {}: {}".format(gpio, gpio.value)

print "Set {} --> {}".format(gpio, 1)
gpio.set_value(1)
print "Read {}: {}".format(gpio, gpio.value)

print "Set {} --> {}".format(gpio, 0)
gpio.set_value(0)
print "Read {}: {}".format(gpio, gpio.value)



