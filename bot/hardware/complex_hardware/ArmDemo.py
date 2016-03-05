import os import sys
from time import sleep
import pyDMCC
from robot_arm import RobotArm
from SeventhDOF import Rail_Mover


arm = RobotArm() 

while True:
 	
	sleep(5)
	arm.rail.DisplacementConverter(3.5)
	sleep(2)
	arm.SetPosition_1()
	sleep(1)
	arm.rail.Orientor(4)
	sleep(1)
	arm.rail.ResetToHome()
	sleep(1)
	arm.rail.DisplacementConverter(3.5)
	arm.SetPosition_2()
	sleep(5)
	arm.rail.ResetToHome()


