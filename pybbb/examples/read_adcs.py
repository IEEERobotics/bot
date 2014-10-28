#!/usr/bin/env python

import sys
import os
from bbb import ADC
import time

adcs = []
for i in range(7):
  adcs.append(ADC(i))

t0 = time.time()
for i in range(7):
    print "[{:0.3f}] {} : {:4}, {:6.1f} mV".format(
            time.time()-t0, adcs[i], adcs[i].raw(), adcs[i].mV)

