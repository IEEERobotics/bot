import generic_blocks
import cv2
import numpy as np
from robot_arm import RobotArm
import bot.lib.lib as lib

sensor_dist = 12.5

arm = RobotArm(lib.get_config('bot/config.yaml'))
arm.reset_home_position()
arm.rail.DisplacementMover(3600)

img = arm.cam.get_current_frame()
offset = generic_blocks.get_lateral_offset(img, sensor_dist)[0]
print 'moving 7th dof', offset, 'inches to the', 'left' if offset<0 else 'right'

arm.rail.DisplacementMover(arm.rail.DisplacementConverter(-offset))

img = arm.cam.get_current_frame()
x, y, z = generic_blocks.get_front_center(img)[0]

print 'block coordinates'
print 'horizontal offset:', x
print 'vertical offset:', y
print 'distance:', z
