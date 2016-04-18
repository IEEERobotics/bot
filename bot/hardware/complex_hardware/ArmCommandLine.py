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
    print "5:  Calibrate rail"
    print "6:  Pinch         "
    print "7:  Let go        "
    print "8:  Reset the arm and rail"
    print "9:  Check color in bin"
    print "10: Tier Grab         "
    print "11: Turn Light On     "
    print "12: dd_check_bin      "
    print "13: Grab QR           "
    print "14: Grab Color        " 
    print "15: Find block with IR"
    print "16: Check Hopper Colors"
    

    Command = input("Command:  ")
    if Command == 16:
        arm.check_hopper()
    
    if Command == 15:
        arm.FindBlockWithIR('B') 
        
    if Command == 13: 
        arm.GrabQR()
        
    if Command == 14:
        arm.GrabColor() 
        
    if Command == 12:
        
        Bin = raw_input("left, back or right:  ")
        arm.dd_check_bin(Bin) 
    
    if Command == 11:
        
        arm.TurnOnLight()
    
    if Command == 10:
        arm.competition_solver_barge('B') 
    
    if Command == -1: 
        print "Good Bye!"
        break
        
    if Command == 1:
        arm.demo_set_angles()
        
    if Command == 2:
        Pos = input("which bin to go to:  ")
        arm.rail.Orientor(Pos)
        
    if Command == 3:
        i = 0
        while i < 4:
            Color = raw_input("Block color:   ") 
            qr = QRCode2(0,Color,0)
            arm.hopper[i]=qr 
            i=i+1   
            
    if Command == 4:
        Color = raw_input("Which color:  ")
        Course = raw_input("which course:  ")
        arm.reset_home_position() 
        arm.FindAndGetBlock(Color,Course)
        
    if Command == 5:
        arm.rail.CalibrateRail() 
        
    if Command == 6: 
        arm.grab()
        
    if Command == 7:
        arm.release()
     
    if Command == 8:
        arm.reset_home_position()
        
    if Command == 9: 
         
        arm.check_hopper()
        print arm.hopper 
    
