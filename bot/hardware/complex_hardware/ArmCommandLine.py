import os 
import sys 
from time import sleep 
import bot.lib.lib as lib 
from robot_arm import RobotArm 
from QRCode2 import QRCode2

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
    print "7:  Test function" 

    Command = input("Command:  ")
    
    if Command == -1: 
        break
    if Command == 2:
        Pos = input("Which bin:  ")
        arm.rail.Orientor(Pos) 
    if Command == 1:
        arm.demo_set_angles()
    if Command == 4:
        Color = raw_input("Which color:  ")
        arm.FindAndGetBlock(Color)
    if Command == 5:
        Tier = raw_input("Which Tier")
        arm.Tier_Grab(Tier)
    if Command == 3:
        i = 0
        while i < 4:
            Color = raw_input("Block color:   ") 
            qr = QRCode2(0,Color,0)
            arm.hopper[i]=qr 
            i=i+1
    if Command == 7:
        arm.TestFunction() 
