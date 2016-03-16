import os 
import sys 
from time import sleep 
import bot.lib.lib as lib 
from robot_arm import RobotArm 


bot_config = lib.get_config()
arm_config = bot_config["dagu_arm"]
arm = RobotArm(arm_config)


while True:
    print "Commands:  " 
    print "1:  Set Angles"
    print "2:  Move to hopper pos"
    print "3:  Set Hopper" 
    print "4:  Empty hopper"  
    print "5:  Grab the block" 

    Command = input("Command:  ")
    
    if Command == -1: 
        break
    if Command == 1:
        arm.demo_set_angles()
    if Command == 5:
        Tier = raw_input("Which Tier")
        arm.Tier_Grab(Tier)
