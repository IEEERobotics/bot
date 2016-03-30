import os, sys
from time import sleep
import pyDMCC

import bot.lib.lib as lib

class Rail_Mover(object):

    def __init__(self):
    
        self.bin_1 = 200
        self.bin_2 = 2600
        self.bin_3 = 4570
        self.bin_4 = 6870 
        self.left_extreme = 7100
        
        self.bot_config = lib.get_config()

        rail_motor_conf = self.bot_config["dagu_arm"]["rail_cape"]["rail_motor"]
        board_num = rail_motor_conf["board_num"]
        motor_num = rail_motor_conf["motor_num"]
        
        self.rail_DMCC = pyDMCC.DMCC(1)    
        self.rail_motor = self.rail_DMCC.motors[motor_num]
    @lib.api_call 
    def Orientor(self,Position):
        
          
        self.rail_motor.power = 0

        if Position == 1:
            Displacement = self.bin_1 - self.rail_motor.position 
            return self.DisplacementMover(Displacement)
            
        elif Position == 2:
            Displacement = self.bin_2 - self.rail_motor.position
            return self.DisplacementMover(Displacement)
            
        elif Position == 3:
            Displacement = self.bin_3 - self.rail_motor.position
            return self.DisplacementMover(Displacement)
        elif Position == 4:
            Displacement = self.bin_4 - self.rail_motor.position
            return self.DisplacementMover(Displacement)

    def DisplacementMover(self,Displacement):

        if (self.rail_motor.position + Displacement) > self.left_extreme:
            print "Cannot move beyond range"
            return 0 
        elif (self.rail_motor.position + Displacement) < 0:
            print "Cannot move beyond range"
            return 0

        StartPOS = self.rail_motor.position
        
        if Displacement == 0:
            return 1
        elif Displacement < 0:   #Negative movement 
            power = 40
            self.rail_motor.power = power
            print self.rail_motor.position
            i = 0 
            while self.rail_motor.position > (StartPOS + Displacement):
                i = i +1 
            print self.rail_motor.position
            
            self.rail_motor.power = 0

        elif Displacement > 0:    #Positive movement
            power = -40
            self.rail_motor.power = power
            print self.rail_motor.position
            i = 0
            while self.rail_motor.position < (StartPOS + Displacement):
                i = i +1     
               
            print self.rail_motor.position
            self.rail_motor.power = 0


        return 1 


    def DisplacementConverter(self,RawDisplacement):  
        
        ConversionRatio = 1020
        Displacement = RawDisplacement*ConversionRatio
        return self.DisplacementMover(Displacement)

    def ResetToHome(self):

        if self.rail_motor.position < 0:
            self.rail_motor.reset()
            return 0

        power = 40
        self.rail_motor.power = power
        i = 0
        while self.rail_motor.position > 20:
            print self.rail_motor.position
            print "velocity: ", self.rail_motor.velocity
        
        self.rail_motor.power = 0
        self.rail_motor.reset()
        return 1
    
    
    def RunIntoWall(self):
        print "I am trying to run into the wall."
        power = 40
        self.rail_motor.power = power
        print "velocity: ", self.rail_motor.velocity
        sleep(.5)
        print "velocity: ", self.rail_motor.velocity
        i = 0
        while self.rail_motor.velocity < 0:
            i = i+1
            
    
        self.rail_motor.power = 0
        self.rail_motor.reset()
        return 1
    
    @lib.api_call 
    def MoveToPosition(self,Position):
        
        current_position = self.rail_motor.position
        
        if Position < 0 or Position > self.left_extreme:
            print "Invalid Position"
            return 0
            
        Displacement = Position - current_position
        
        self.DisplacementMover(Displacement) 
    @lib.api_call
    def CalibrateRail(self):
        Delta = 100
        while True:
            command = raw_input("A:Right F:Left") 
            if command == 'A':
                self.DisplacementMover(-Delta)
            if command == 'F':
                self.DisplacementMover(Delta)
            if command == 'C':
                self.bin_1 = input("bin 1 value:  ")
                self.bin_2 = input("bin 2 value:  ") 
                self.bin_3 = input("bin 3 value:  ")
                self.bin_4 = input("bin 4 value:  ") 
                self.left_extreme = input("left extreme value:  ") 
            if command == 'Q':
                break 
        
    def SetMotorPower(self):
        
        self.rail_motor.power = -50 
     
    def StopMotor(self):
        self.rail_motor.power = 0 
        

