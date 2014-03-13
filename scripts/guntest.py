#!/usr/bin/env python

import os, sys
from pprint import pprint
import pyDMCC
from time import sleep, time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('power', type=int)
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

print "Autodetecting DMCCs...",
dmccs = pyDMCC.autodetect()
print "  found:", len(dmccs)

gun_dmcc = dmccs[2]  # Wheel gun motors are always on 2
left = gun_dmcc.motors[2]
right = gun_dmcc.motors[1]

# Reset the QEI position counters
left.reset()
right.reset()

# NOTE: One power must always be inverted!!
power = args.power
print "Setting power to:", power
left.power = -power
right.power = power

t0 = time()
print "Press <control-c> to stop"

period = 2.0
left_last_pos = 0
right_last_pos = 0
while True:
    sleep(period)
    left_pos = left.position
    right_pos = right.position
    left_delta = left_pos - left_last_pos
    right_delta = right_pos - right_last_pos
    left_last_pos = left_pos
    right_last_pos = right_pos
    #print "[{:0.3f}] Voltage: {:0.2f}, Current: {:3d} | {:3d}, Position: {:6d} | {:6d}, Velocity: {:3d} | {:3d}".format(
    #       time()-t0, dmcc.voltage, left.current, right.current, left.position, right.position, left.velocity, right.velocity)
    print "{:7.3f} DMCC : Voltage: {:0.2f}".format(time()-t0, gun_dmcc.voltage)
    print "       Left : Current: {:3d}, Position: {:6d}, Velocity: {:3d}, Calc_vel: {:0.1f}".format(
           left.current, left_pos, left.velocity, left_delta/period)
    print "       Right: Current: {:3d}, Position: {:6d}, Velocity: {:3d}, Calc_vel: {:0.1f}".format(
           right.current, right_pos, right.velocity, right_delta/period)
     
