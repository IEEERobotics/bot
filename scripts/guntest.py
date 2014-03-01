#!/usr/bin/env python

import os, sys
from pprint import pprint
import pyDMCC
from time import sleep
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('speed', type=int)
parser.add_argument('-l', '--left', action='store_true', default=False)
parser.add_argument('-r', '--right', action='store_true', default=False)
args = parser.parse_args()

import signal
from time import time,sleep

def cleanup(signum, frame):
    print "Powering down..."
    for d in dmccs.values():
        for m in d.motors.values():
            m.power = 0
    exit(0)

signal.signal(signal.SIGINT, cleanup)

print "Autodetecting DMCCs..."
dmccs = pyDMCC.autodetect()

print "  ...found:", len(dmccs)

power = args.speed
print "Setting power to:", power

dmcc = dmccs[1]
right = dmcc.motors[1]
left = dmcc.motors[2]

right.power = power
left.power = -power

print "Press <control-c> to stop"
while True:
    sleep(0.2)
    print "Voltage: {:0.2f}, Left: {:3d} ({:3d} mA), Right: {:3d} ({:3d} mA)".format(
           dmcc.voltage, left.velocity, left.current, right.velocity, right.current )
    

