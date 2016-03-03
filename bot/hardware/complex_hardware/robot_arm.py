

"""Encapsulates functionality of moving around robot arm"""
import os

import zbar
from PIL import Image
import cv2
import numpy as np
import time

import bot.lib.lib as lib
from bot.hardware.servo_cape import ServoCape

from bot.hardware.qr_code import QRCode
from bot.hardware.complex_hardware.QRCode2 import QRCode2
from SeventhDOF import Rail_Mover
from bot.hardware.complex_hardware.camera_reader import Camera



class RobotArm(object):

    JUNK_BUFFER = [0]*5
    HOME = [0, 145, 0, 160, 0]
    GRAB = 5


    """An object that resembles a robotic arm with n joints"""
    def __init__(self, arm_config):
        
        self.logger = lib.get_logger()
        self.bot_config = lib.get_config()
        
        self.servo_cape \
            = ServoCape(self.bot_config["dagu_arm"]["servo_cape_arm"])     
        self.servo_cape_grabber \
            = ServoCape(self.bot_config["dagu_arm"]["servo_cape_grabber"])     
        
        # QR scanning tools.
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')

        # Figure out what camera is being used
        cam_model = arm_config["camera"]
        self.cam = Camera(self.bot_config[cam_model])
        self.rail = Rail_Mover()  
        
        # initialize vertices of QR code
        l = 1.5
        self.qr_verts = np.float32([[-l/2, -l/2, 0],
                            [-l/2,  l/2, 0],
                            [ l/2, -l/2, 0],
                            [ l/2,  l/2, 0]])

        # Angles of all of the joints. 
        # DO NOT SEND ANGLES ANY OTHER WAY
        self.joints = self.HOME

        self.hopper = [None, None, None, None]

    @property
    def joints(self):
        return self.__joints

    @joints.setter
    def joints(self, vals):
        vals =  [int(x) for x in vals]
        # validate values
        if len(vals) == 5:
            self.__joints = vals
        else:
            self.__joints[:len(vals)] = vals
        print "Joints to be sent: ", vals
        self.servo_cape.transmit_block([0] + self.__joints)


    @lib.api_call
    def draw_qr_on_frame(self, zbar_dat, draw_frame):

        self.scanner.scan(zbar_dat)
        for symbol in zbar_dat:
            tl, bl, br, tr = [item for item in symbol.location]
            points = np.float32([[tl[0], tl[1]],
                                 [tr[0], tr[1]],
                                 [bl[0], bl[1]],
                                 [br[0], br[1]]])

            cv2.line(draw_frame, tl, bl, (100,0,255), 8, 8)
            cv2.line(draw_frame, bl, br, (100,0,255), 8, 8)
            cv2.line(draw_frame, br, tr, (100,0,255), 8, 8)
            cv2.line(draw_frame, tr, tl, (100,0,255), 8, 8)

        return draw_frame
    @lib.api_call
    def grab(self):
 
        self.servo_cape_grabber.transmit_block([5] + self.JUNK_BUFFER)
        
    @lib.api_call   
    def release(self):
        self.servo_cape_grabber.transmit_block([6] + self.JUNK_BUFFER)
        
    @lib.api_call
    def joint_center_on_qr(self):
        """Attempts to center arm on qr code using only arm itself.
        Only the rotational joints, 
        joint 0 corrects X 
        joint 3 corrects Y
        joint 5 corrects rotation
        """
        
        # Correction constants for P(ID) controller.
        # unlikely that we'll bother using I or D
        p_x = 1
        p_y = 1

        while True:
            ret = self.cam.QRSweep()
            
            # Calculate new vector for change
            if ret != None:
                
                dx = ret.tvec[0]
                dy = ret.tvec[1]
                
                if abs(dx) > 0.2:
                    self.joints[0] += p_x * dx
                if abs(dy) > 0.2:
                    self.joints[3] += p_y * dy
                #print "Joints = ", self.joints
                self.joints = self.joints
                #TODO Find method for calculating rotational oreientation

        return True

    @lib.api_call
    def demo_set_angles(self):
        while(1):
            A1 = (input("What is Servo 1's angle?: "))
            if (A1 < 0 or A1> 180):
                print "Error: Given angle is out of range."
                continue
            else:
                break
                
        while(1):
            A2 = (input("What is Servo 2's angle?: "))
            if (A2 < 0 or A2> 180):
                print "Error: Given angle is out of range."
                continue
            else:
                break
                
        while(1):
            A3 = (input("What is Servo 3's angle?: "))
            if (A3 < 0 or A3> 180):
                print "Error: Given angle is out of range."
                continue
            else:
                break
                
        while(1):
            A4 = (input("What is Servo 4's angle?: "))
            if (A4 < 0 or A4> 180):
                print "Error: Given angle is out of range."
                continue
            else:
                break
                
        while(1):
            A5 = (input("What is Servo 5's angle?: "))
            if (A5 < 0 or A5> 180):
                print "Error: Given angle is out of range."
                continue
            else:
                break
                
        while(1):
            answer = raw_input("Do you want to send these angles(y/n)?: ")
            if (answer == 'n'):
                return
            elif (answer == "y"):
                array = [A1,A2,A3,A4,A5]
                self.servo_cape.transmit_block([0] + array)
                return
            else:
                print "Error: Invalid reply. Please answer in y/n format."
        
        
        
    @lib.api_call
    def reset_home_position(self):
        """
        sets angles back to default position. Also resets the position of the 7th DOF
        """
        self.servo_cape.transmit_block([0] + HOME)
        self.rail.RunIntoWall()
        
    @lib.api_call
    def fancy_demo(self):
        os.system('clear')
        print "Welcome to the Team 26: Robotic Arm Mainipulation and Vision demo function."
        print "Demo number      Function       "
        print "1                Input custom angles"
        print "2                Block grap demo"
        print "3                Wave"
        print "4                Stand up straight"
        print "5                Grab"
        print "6                Release"
        print "7                Show range of servos"
        print "8                Initial position"
        print "9                Exit"
        print ""
        while(1):
            demo_number = (input("Please input your desired operation number: "))
            if (demo_number is "exit"):
                return
            elif (demo_number > 9 or demo_number < 0):
                print "Number not within valid range (1-9)."
                continue
            elif (demo_number == 9):
                return
            elif (demo_number == 1):
                self.set_angles()
            else:
                self.demo(demo_number - 1)
        
    @lib.api_call
    def demo(self, demo_number):
        """runs demos 1-7"""
        self.servo_cape.transmit_block([demo_number]
                                         + self.JUNK_BUFFER)        
    
    
    def rail_test(self):
        
        while True:
            #time.sleep(2)
            ret = self.cam.QRSweep()
            if ret != None:
                x_disp = ret.tvec[0]
                print "Checking Alignment with x_disp = ", x_disp
                if abs(x_disp) > .2:
                    self.rail.DisplacementConverter(-1 * x_disp)
            
            ret = None
            
    def rail_feedback(self):
        """
        align the arm on the rail to a qrcode and return the code
        """
        count = 0
        direction = 1
        while(True):
            ret = None
            ret = self.cam.QRSweep()
            if ret != None:
                count = 0                           #reset the count.
                x_disp = ret.tvec[0]
                if abs(x_disp) < .1:
                    return ret
                else:
                    print "Checking Alignment with x_disp = ", x_disp
                    if abs(x_disp) > .1:
                        rail_ret = self.rail.DisplacementConverter(-1 * x_disp)
                        if rail_ret == 0:
                            #out of range, reset to middle and try again
                            disp = self.rail.DMCC[1].motors[2].position
                            ticks = 3000 - disp
                            self.rail.DisplacementMover(ticks)
            else:                                   # if no qrcodes are found
                if count >= 8:
                    count = 0
                    limit = self.rail.DisplacementConverter(1.5*direction)
                    if limit == 0:                  #out of range
                        direction = -1*direction    #reverse direction
                        ret = self.rail.DisplacementConverter(.75*direction)
                        if ret == 0:
                            print "Error: out of range on both ends, shouldn't be possible."
                            
                count += 1
                
    
    def test_look(self):
        self.servo_cape.transmit_block([0] + [0, 125, 0, 170, 0])
    
    def basic_solver(self):
        i = 4
        while(i>0):
            self.joints = self.HOME
            self.rail.RunIntoWall()
            time.sleep(4)
            self.Tier_Grab('B')
            i= i-1
        
    
    def Tier_Grab(self, Tier):
        if Tier == 'A':
            print "Not coded yet" 
            BLOCK_MOVE_5 = [0, 90, 90, 90, 0]
            BLOCK_GRAB_5 = [0, 90, 90, 90, 0]

        elif Tier == 'B':
            BLOCK_MOVE_5 = [0, 80, 10, 100, 0]
            BLOCK_GRAB_5 = [0, 74, 10, 100, 0]
            LOOK_5 = [0, 135, 0, 160, 0]
            HOPPER1 = [0, 78, 10, 0, 180]
            HOPPER2 = [0, 0, 180, 0, 180]
            HOPPER3 = [0, 40, 180, 0, 180]

        elif Tier == 'C':
            BLOCK_MOVE_5 = [0, 60, 20, 40, 0]
            BLOCK_GRAB_5 = [0, 0, 10, 50, 0]
            LOOK_5 = [0, 115, 0, 150, 0]
            HOPPER1 = [0, 0, 10, 0, 180]
            HOPPER2 = [0, 0, 180, 0, 180]
            HOPPER3 = [0, 40, 180, 0, 180]


        time.sleep(1)
        self.servo_cape.transmit_block([0] + LOOK_5)
        time.sleep(2)
        self.rail.DisplacementConverter(3.5)  #get the rail to the middle

        if Tier == 'B' or Tier == 'C':
            qr = self.rail_feedback()           #position infront of QRCode
        else:
            ##Todo: Add in generic block code here 
            print "Line up with generic blocks" 

        hopper_pos = 5

        if self.hopper[0] == None:
            hopper_pos = 1
        elif self.hopper[1] == None:
            hopper_pos = 2
        elif self.hopper[2] == None:
            hopper_pos = 3
        elif self.hopper[3] == None:
            hopper_pos = 4	
        else:
            print "error~Hopper Full"
            return 0 

        self.servo_cape.transmit_block([0] + BLOCK_MOVE_5)
        time.sleep(2.25)                     #wait for arm to move to location
        self.servo_cape.transmit_block([0] + BLOCK_GRAB_5)
        time.sleep(2.25)                     #wait for arm to move to location
        self.grab()
        time.sleep(1.25)                       #wait for arm to grab
        self.servo_cape.transmit_block([0] + HOPPER1)
        time.sleep(1.5)                       #wait for arm to move to location
        self.servo_cape.transmit_block([0] + HOPPER2)
        time.sleep(3)                     #wait for arm to move to location
        self.rail.Orientor(hopper_pos)
        time.sleep(.25)                     #wait for rail to move to bin location
        self.servo_cape.transmit_block([0] + HOPPER3)
        time.sleep(1.5)                     #wait for arm to move to location

        self.release()
        time.sleep(1) 

        self.hopper[hopper_pos-1] = qr
        
        print self.hopper[hopper_pos-1].value
        print self.hopper
        

    def FindAndGetBlock(self,color):
        """ 
        Function which takes a given color, and gets that block out of the hopper
        """
        if self.hopper[0] != None:
            if self.hopper[0].value == color
                self.EmptyHopper(1) 
                self.reset_home_positon()
                
        elif self.hopper[1] != None:
            if self.hopper[1].value == color 
                self.EmptyHopper(2)
                self.reset_home_position()
                
        elif self.hopper[2] != None:
            if self.hopper[2].value == color:
                self.EmptyHopper(3)
                self.reset_home_position()
            
        elif self.hopper[3] != None:
            if self.hopper[3].value == color:
                self.EmptyHopper(4)
                self.reset_home_position()
            	
        else:
            print "No blocks in the hopper" 
            return 0 
        
        return 1 
        
    def EmptyHopper(self,Bin)
        print "not done yet"
        return 0 
        
        
    
