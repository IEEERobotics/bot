"""Logic for line following."""

import sys

import lib.lib as lib
import hardware.ir_hub as ir_hub_mod
import driver.mec_driver as mec_driver_mod
import lib.exceptions as ex


class PIDFollower(object):

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build Ir arrays, logger and drivers."""
        self.logger = lib.get_logger()
        self.irs = ir_hub_mod.IRHub()
        self.driver = mec_driver_mod.MecDriver()
        self.front_reading = 0;
        self.back_reading = 0;        
        self.left_reading = 0;       
        self.right_reading = 0;        
        self.front_position = [0, 0, 0, 0]
        self.back_position = [0, 0, 0, 0]        
        self.left_position = [0, 0, 0, 0]       
        self.right_position = [0, 0, 0, 0]        
        self.current_heading = 0;
        self.front_ke = 1
        self.front_kd = 1
        self.front_ki = 1
        self.back_ke = 1
        self.back_kd = 1
        self.back_ki = 1
        
    def follow(self, state_table):
        """Accept and handle fire commands.

        TODO(dfarrell07): This is a stub

        :param cmd: Description of fire action to execute.
        
        """
        self.state_table = state_table
        # assign the arrays to the correct heading
        self.assign_arrays()
        # calculate the postion of the forward and back sensers
        self.calculate_postion()
        # call front PID
        self.front_pid()
        # call back PID
        self.back_pid() 
        
    def front_pid(self):
        """ calculate the k value for the forward pid"""
        pass
        #p_error = self.front_ke*(heading - self.front_positon[1])
        #d_error = self.front_kd*(self.front_positon[1] - self.front_positon[2])/sampleing_time
        #intergration_error = (self.front_postion[1] + self.front_postion[2])/2*sampling_time + last_intergration_error
        #last_intergration_error = inter
        #I_error = self.front_ki*((self.front_positon[1] + self.front_positon[2])/2*sampling_time + last )
        #return p_error + d_error + I_error  

    def back_pid(self):
        """ calculate the k value for the back pid"""
        pass
                
    def calculate_postion(self):
        """ calculate the postion of the line as it is on the bot"""
        # get rid of the last entry
        self.front_position = self.front_position[:len(self.front_position)-1]
        # add current reading to the list
        self.front_position.insert(0,self.front_reading)       
        # get rid of the last entry
        self.front_position = self.front_position[:len(self.front_position)-1]
        # add current reading to the list
        self.front_position.insert(0,self.back_reading) 
        
    def assign_arrays(self):
       """ take 4 by 16 bit arrays and assigns the array to front back and left and right"""
       self.heading = self.state_table.currentHeading
       current_ir_reading = self.irs.read_all_arrays()  
       # heading west      
       if self.heading == 0:   
           # forward is on the left side                                            
           self.front_reading = self.get_postion_lr(current_ir_reading["left"])
           # back is on the right side  
           self.back_reading = self.get_postion_rl(current_ir_reading["right"])
           # left is on the back  
           self.left_reading = self.get_postion_lr(current_ir_reading["back"])  
           # right is on the fornt
           self.right_reading = self.get_postion_rl(current_ir_reading["front"])
       # heading east   
       elif self.heading == 180: 
           # forward is on the right side                                         
           self.front_reading = self.get_postion_lr(current_ir_reading["right"]) 
           # back is on the left side 
           self.back_reading = self.get_postion_rl(current_ir_reading["left"])  
           # left is on the front
           self.left_reading = self.get_postion_lr(current_ir_reading["front"])  
           # right is on the back
           self.right_reading = self.get_postion_rl(current_ir_reading["back"])  
       # heading south    
       elif self.heading == 270:  
           # forward is on the front side                                          
           self.front_reading = self.get_postion_lr(current_ir_reading["front"]) 
           # back is on the back side
           self.back_reading = self.get_postion_rl(current_ir_reading["back"])   
           # left is on the left
           self.left_reading = self.get_postion_lr(current_ir_reading["left"])   
           # right is on the right 
           self.right_reading = self.get_postion_rl(current_ir_reading["right"])  
           # heading nouth
       elif self.heading == 90:                                                 
           # forward is on the right side
           self.front_reading = self.get_postion_lr(current_ir_reading["back"])  
           # back is on the left side
           self.back_reading = self.get_postion_rl(current_ir_reading["front"])  
           # left is on the front
           self.left_reading = self.get_postion_lr(current_ir_reading["right"])  
           # right is on the back
           self.right_reading = self.get_postion_rl(current_ir_reading["left"])   
        
    def get_postion_lr(self, array):
        """ returns a postion in bits from left to right """
        # set initial postion
        postion = 0                                                             
        # set initial sener hits
        postion_count = 0                                                       
        # move through the list and look for hits
        for n, v in enumerate(array):                                           
            # count the if there is a hit
            if(v == 1):                                                          
                # count the number of hits
                postion_count  = postion_count + 1  
                # add the postion to the last postion  
                postion = postion + v*(15.-n)*12/15
        # if there ate more than 3 hits than stop line following
        if(postion_count > 3):
            # return error condition
            return -1
        # if there is only one hit
        elif(postion_count == 1):     
            # return the postion
            return postion
        # if there are no hits
        elif(postion_count == 0):
            # return 0
            return 0
        # if there at more than one and less than 3 hits find the avarge
        else:
            # return the avarge
            return postion/postion_count

    def get_postion_rl(self, array):
        """ returns a postion in bits from right to left"""
        # set initial postion
        postion = 0
        # set initial hit count to 0
        postion_count = 0
        # move through the list and look for hits
        for n, v in enumerate(array):
            # if there is a hit
            if(v == 1):
                # count the number of hits
                postion_count  = postion_count + 1
                # add the postion to the postion
                postion = postion + v*(n+0.0)*12/15
        # if there are more than 4 hits
        if(postion_count > 3):
            # return error condition
            return -1
        # if there is one condition
        elif(postion_count == 1):
            # return the postion
            return postion
        elif(postion_count == 0):
            return 0
        # if there are less than 4 hits and more than one hit
        else:
            # return the average postion
            return postion/postion_count



