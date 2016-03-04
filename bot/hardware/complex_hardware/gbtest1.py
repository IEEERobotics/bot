import generic_blocks
import cv2
import numpy as np
from robot_arm import RobotArm
import bot.lib.lib as lib
from time import sleep
from SeventhDOF import Rail_Mover

sensor_dist = 12.5

cam = cv2.VideoCapture(-1)
cam.set(3, 320)
cam.set(4, 240)

def read():
	for i in range(4):
		cam.grab()
	return cam.read()[1]

rail = Rail_Mover()
rail.RunIntoWall()
print 'home reset'
sleep(.1)
rail.DisplacementMover(3600)

#raw_input('in neutral position, press enter to align with block')

for i in range(2):
	img = read()
	offset = generic_blocks.get_lateral_offset(img, sensor_dist)[0]
	print 'need to move 7th dof', abs(offset), 'inches to the', 'left' if offset<0 else 'right'

#try: input('press enter to continue...')
#except: pass

	rail.DisplacementMover(rail.DisplacementConverter(-offset))

#	sleep(.5)

img = read()
x, y, z = generic_blocks.get_front_center(img)[0]

print 'block coordinates'
print 'horizontal offset:', x
print 'vertical offset:', y
print 'distance:', z
