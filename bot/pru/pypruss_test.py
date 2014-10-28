#!/usr/bin/env python

import sys
import signal
import pypruss
import mmap
import struct

def cleanup(signum, frame):
    pypruss.pru_disable(0)
    pypruss.exit()                                # Exit
    sys.exit()

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

pru_addr = 0x4a300000
PRU_EVOUT_0 = 0
PRU0_ARM_INTERRUPT = 19

with open("/dev/mem", "r+b") as f:	            # Open the memory device
    mem = mmap.mmap(f.fileno(), 32, offset=pru_addr) # mmap the right area

pypruss.init()    # Init the PRU
try:
    pypruss.open(0)  # Open PRU event 0 which is PRU0_ARM_INTERRUPT
except SystemError as e:
    print e
    print "Is the PRU module (uio_pruss) loaded?"

pypruss.pruintc_init()  # Init the interrupt controller
pypruss.exec_program(0, "./ultrasonic.bin")

while True:
    print "Wait for event... ",
    pypruss.wait_for_event(PRU_EVOUT_0)
    print "Got event"
    pypruss.clear_event(PRU_EVOUT_0,PRU0_ARM_INTERRUPT)
    time1, pre1, time2, pre2, time3, pre3, time4, pre4 = struct.unpack_from('LLLLLLLL', mem, 0)
    print "Vals:"
    print "  %d, %d = %0.2f in" % (pre1, time1, time1/149.3)
    print "  %d, %d = %0.2f in" % (pre2, time2, time2/149.3)
    print "  %d, %d = %0.2f in" % (pre3, time3, time3/149.3)
    print "  %d, %d = %0.2f in" % (pre4, time4, time4/149.3)

    print "Wait for event2... ",
    pypruss.wait_for_event(PRU_EVOUT_0)
    print "Got event"
    pypruss.clear_event(PRU_EVOUT_0,PRU0_ARM_INTERRUPT)

