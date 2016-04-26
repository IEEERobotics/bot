import os 
from time import sleep
import bot.hardware.complex_hardware.robot_arm as RA 
import bot.lib.lib as lib 

bot_config = lib.get_config()

arm_config = bot_config["dagu_arm"] 

arm = RA.RobotArm(arm_config) 



arm.competition_solver_barge('B')
