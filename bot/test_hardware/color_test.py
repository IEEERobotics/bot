import os
from time import sleep
import bot.hardware.complex_hardware.robot_arm as RA
import bot.lib.lib as lib

bot_config = lib.get_config()

arm_config = bot_config["dagu_arm"]

arm = RA.RobotArm(arm_config)

print "X = ", arm.cam.resX
print "Y = ", arm.cam.resY

while True:
    arm.cam.QRSweep()

sleep(2)
arm.rail.DisplacementConverter(3.5)
sleep(1)
arm.check_block_color(3)
sleep(2)
arm.reset_home_position()
sleep(4)
