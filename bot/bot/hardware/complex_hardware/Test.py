import os, sys
from time import sleep
from robot_arm import RobotArm 

arm = RobotArm("dagu_arm")

while True:
    arm.servo_cape.transmit_block([1]+[0,0,0,0,0])
    sleep(10)

