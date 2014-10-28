#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.abspath('.'))
import bbb.adc as adc

adcs = []
for i in range(7):
    adcs.append(adc.adc(i))

for i in range(7):
    print "%s : %d " % (adcs[i], adcs[i].read())
