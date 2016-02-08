import os, sys
from time import sleep
import pyDMCC


class Rail_Mover:

    def __init__(self):
        self.DMCC = pyDMCC.autodetect()
        

    
    def Orientor(self,Position):
        
          
        self.DMCC[1].motors[2].power = 0

        if Position == 1:
            Displacement = 200 - self.DMCC[1].motors[2].position 
            return self.DisplacementMover(Displacement)
            
        elif Position == 2:
            Displacement = 2200 - self.DMCC[1].motors[2].position
            return self.DisplacementMover(Displacement)
            
        elif Position == 3:
            Displacement = 4600 - self.DMCC[1].motors[2].position
            return self.DisplacementMover(Displacement)
        elif Position == 4:
            Displacement = 7200 - self.DMCC[1].motors[2].position
            return self.DisplacementMover(Displacement)

        

        
 


    def DisplacementMover(self,Displacement):

        if (self.DMCC[1].motors[2].position + Displacement) > 7200:
            print "Cannot move beyond range"
            return 0 
        elif (self.DMCC[1].motors[2].position + Displacement) < 0:
            print "Cannot move beyond range"
            return 0

        StartPOS = self.DMCC[1].motors[2].position
        
        if Displacement == 0:
            return 1
        elif Displacement < 0:   #Negative movement 
            power = 40
            self.DMCC[1].motors[2].power = power

            while self.DMCC[1].motors[2].position > (StartPOS + Displacement):
                print self.DMCC[1].motors[2].position
            
            self.DMCC[1].motors[2].power = 0

        elif Displacement > 0:    #Positive movement
            power = -40
            self.DMCC[1].motors[2].power = power

            while self.DMCC[1].motors[2].position < (StartPOS + Displacement):
                print self.DMCC[1].motors[2].position

            self.DMCC[1].motors[2].power = 0


        return 0 


    def DisplacementConverter(self,RawDisplacement):  
        
        ConversionRatio = 1020
        Displacement = RawDisplacement*ConversionRatio
        return self.DisplacementMover(Displacement)
        



    def ResetToHome(self):

        if self.DMCC[1].motors[2].position < 0:
            self.DMCC[1].motors[2].reset()
            return 0

        power = 40
        self.DMCC[1].motors[2].power = power
        while self.DMCC[1].motors[2].position > 20:
            print self.DMCC[1].motors[2].position
        
        self.DMCC[1].motors[2].power = 0
        self.DMCC[1].motors[2].reset()
        return 1

