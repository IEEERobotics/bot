
"""Encapsulates functionality of moving around robot arm"""

from bot.hardware.IR import IR 

import os

import zbar
from PIL import Image
import cv2
import numpy as np
import time

import bot.lib.lib as lib
from bot.hardware.servo_cape import ServoCape

from bot.hardware.qr_code import QRCode
from QRCode2 import QRCode2, Block 

from SeventhDOF import Rail_Mover
from bot.hardware.complex_hardware.camera_reader import Camera
import pyDMCC 

import generic_blocks



JUNK_BUFFER = [0]*5
HOME = [0, 25, 170, 0, 180]
GRAB = 5


class RobotArm(object):

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
        self.joints = HOME

        self.hopper = [None, None, None, None]
        self.bins = [None, None, None]
        
        self.IR = IR()
        #self.cam.start()

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
            print "Error: Joints requires 5 Angles."
            return
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
 
        self.servo_cape_grabber.transmit_block([5] + JUNK_BUFFER)
        
    @lib.api_call   
    def release(self):
        self.servo_cape_grabber.transmit_block([6] + JUNK_BUFFER)

    @lib.api_call
    def set_joints(self, a0=None
                    , a1=None
                    , a2=None
                    , a3=None
                    , a4=None):
        set_vals = [a0, a1, a2, a3, a4]
        for i in range(len(set_vals)):
            if set_vals[i] != None:
                self.joints[i] = set_vals[i]
        self.joints = self.joints
        
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
        p_x = 10
        p_y = 10

        while True:
            ret = self.cam.QRSweep()
            
            # Calculate new vector for change
            if ret != None:
                
                dx = ret.tvec[0]
                dy = ret.tvec[1]
                
                if abs(dx) > 0.1:
                    self.joints[0] += p_x * dx
                if abs(dy) > 0.1:
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
        self.release()
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
                                         + JUNK_BUFFER)        
            
    def rail_feedback(self):
        """
        align the arm on the rail to a qrcode and return the code
        else when it cannot find a QRCode 4 or more times it will return None.
        """
        giveup = 0
        count = 0
        direction = 1
        self.cam.start()
        time.sleep(2)
        while(True):
            x = 0
            QRList = []
            while (x < 3):
                x = x + 1
                ret = None
                time.sleep(1)           #sleep to update the camera a bit.
                partial_list = self.cam.partial_qr_scan()
                ret = self.cam.partial_qr_select(partial_list)
                if ret != None:
                    x_disp = ret.tvec[0]
                    if abs(x_disp) < .15:
                        print "QRCode found at x_disp: ", x_disp
                        self.cam.stop()
                        return ret
                    else:
                        QRList.append(ret)
                        print "Checking Alignment with x_disp = ", x_disp
                        print "countx = ", x
                            
            targetQR = self.cam.selectQR(QRList)
            if targetQR != None:
                rail_ret = self.rail.DisplacementConverter(targetQR.tvec[0])
                if rail_ret == 0:
                    #out of range, reset to middle and try again
                    self.rail.MoveToPosition(3500)
            else:       # if no qrcodes are found
                limit = self.rail.DisplacementConverter(1.5*direction)
                if limit == 0:                  #out of range
                    direction = -1*direction    #reverse direction
                    ret = self.rail.DisplacementConverter(.75*direction)
                    if ret == 0:
                        print "Error: out of range on both ends, shouldn't be possible."   
    
    def test_look(self):
        self.servo_cape.transmit_block([0] + [0, 125, 0, 170, 0])
    
    def basic_solver(self):
        i = 4
        while(i>0):
            self.joints = HOME
            self.rail.RunIntoWall()
            time.sleep(4)
            self.Tier_Grab('B')
            i= i-1
           
    @lib.api_call 
    def MoveToQR(self):
    
        LOOK = [0, 15, 170, 10, 180]
        time.sleep(1)
        self.servo_cape.transmit_block([0] + HOME)
        time.sleep(2)
        #get the rail to the middl
        self.rail.DisplacementConverter(3.5)
        # In front of QR  
        qr = self.rail_feedback()           
        return qr

    def MoveToGenericBlock(self):
        block_dist = 12.5 #adjust to correct block distance from camera
        self.rail.DisplacementMover(3600 - self.rail.rail_motor.position) #goto middle
        for i in xrange(1): #potentially move multiple times to get it right
            img = self.cam.get_current_frame() #needs to be bottom camera
            offsets = generic_blocks.get_lateral_offset(img, block_dist)
            if len(offsets) == 0: return 0
            self.rail.DisplacementConverter(-offsets[0])
        return 1
    
    @lib.api_call
    def Tier_Grab(self, Tier, Case):
           ### Tier is the level of the barge the block is being grabbed from
           ### Case is whether or not a block is on top of another
        #if Tier == 'B' or Tier == 'C':
        #    qr = self.MoveToQR()
         
        if Tier == 'A':
            ## Generic Blocks 
            print "Not coded yet" 
            
            self.joints = [0,60,125,85,180]
            time.sleep(3)
            if Case == 1:
            
                BLOCK_MOVE_5 = [0, 105, 135, 50, 180]
            if Case == 2: 
                BLOCK_MOVE_5 = [0, 105, 110, 35, 180]
                LOOK_5 = [0, 25, 170, 10, 180]
                        
            HOPPER1 = [0, 45, 145, 55, 180]
            HOPPER2 = [0, 55, 165, 0, 180]
        elif Tier == 'B':
            self.joints = [0,70,145,60,180]
            time.sleep(3)
            ## Mixed QR Blocks 
            if Case == 1:  ## Block on top
                BLOCK_MOVE_5 = [0, 85, 160, 70, 180]
            elif Case == 2: ## Block on bottom
                BLOCK_MOVE_5 = [0, 90, 170, 60, 180]
                
            LOOK_5 = [0, 25, 170, 10, 180]
            HOPPER1 = [0, 45, 145, 35, 180]
            HOPPER2 = [0, 40, 170, 0, 180]
            

        elif Tier == 'C':
            BLOCK_MOVE_5 = [0, 60, 20, 40, 0]
            BLOCK_GRAB_5 = [0, 0, 10, 50, 0]
            LOOK_5 = [0, 25, 170, 10, 180]
            HOPPER1 = [0, 90, 100, 45, 180]
            HOPPER3 = [0, 40, 180, 0, 180]







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
        time.sleep(2)                     #wait for arm to move to location
        self.grab()
        time.sleep(2)                       #wait for arm to grab
        self.servo_cape.transmit_block([0] + HOPPER1)

        time.sleep(2)                     #wait for arm to move to location
        self.rail.Orientor(hopper_pos)
        time.sleep(2)                     #wait for rail to move to bin location
        self.joints = HOME
        time.sleep(2)                       #wait for arm to move to location
        self.servo_cape.transmit_block([0] + HOPPER2)
        time.sleep(2) 

        self.release()
        time.sleep(1) 

        self.hopper[hopper_pos-1] = QRCode2(0,"None",0) 
        
      
    @lib.api_call
    def FindAndGetBlock(self,color):
        """ 
        Function which takes a given color, and gets that block out of the hopper
        """
        self.reset_home_position() 
        if self.hopper[0] != None:
            if self.hopper[0].value == color:
                self.EmptyHopper(1) 
                
                time.sleep(4)
                
                
        if self.hopper[1] != None:
            if self.hopper[1].value == color: 
                self.EmptyHopper(2)
                
                time.sleep(4)
                
        if self.hopper[2] != None:
            if self.hopper[2].value == color:
                self.EmptyHopper(3)
                
                time.sleep(4)
                
            
        if self.hopper[3] != None:
            if self.hopper[3].value == color:
                self.EmptyHopper(4)
                time.sleep(4)
            	
        else:
            print "No blocks in the hopper" 
            return 0 
        self.reset_home_position()
        return 1 
        
    @lib.api_call
    def EmptyHopper(self,hopper_pos,Course):

        Hopper = [0,85,170,20,180]
        PullBack = [0,35,170,30,180]
        if(Course == "right"):
            OffSide = [85,65,110,10,180]
            self.reset_home_position()
            self.rail.Orientor(hopper_pos)
            time.sleep(1)
            self.servo_cape.transmit_block([0] + Hopper)
            time.sleep(3)
            self.grab() 
            time.sleep(2)
            self.joints = HOME
            time.sleep(6)
            if hopper_pos != 1:
                self.rail.Orientor(1)
            self.servo_cape.transmit_block([0] + OffSide) 
            time.sleep(6)
            self.release()
            time.sleep(1.5)
            self.joints = HOME
            time.sleep(7)
            
        if(Course == "left"):
            self.reset_home_position()
            self.rail.Orientor(hopper_pos)
            time.sleep(1)
            self.servo_cape.transmit_block([0] + Hopper)
            time.sleep(3)
            self.grab()
            time.sleep(5)
            self.joints = HOME
            time.sleep(4) 
            if hopper_pos!= 4:
                self.rail.Orientor(4) 
                
            time.sleep(2)
            self.servo_cape.transmit_block([0] + PullBack) 
            time.sleep(3)       

            time.sleep(3)
            self.joints = [85,90,60,160,0]
            time.sleep(8)
            self.release() 
            time.sleep(1.5)
            self.joints = HOME
<<<<<<< HEAD
            time.sleep(8)
=======
            time.sleep(9)
>>>>>>> 282a96c8c154432b4a24bb81ccc1209bc4eb2a54
        
        self.hopper[hopper_pos-1] = None 
        
        return 1 
        
        
    @lib.api_call   
    def check_block_color(self, hopper_pos):
        """
        Takes the hopper posisiton 0-3 as input and will look at the hopper posistion
        to see what clor it is then update the hopper array with the new data.
        """

        HOPPER_LOOK = [0,75,140,10,180]


        #look at the hopper physically
        self.rail.Orientor(hopper_pos + 1)
        self.joints = HOPPER_LOOK
        time.sleep(3)
        #look for a color
        largest = self.GrabColor()
        #udate with color found
        if largest != None:
            if self.hopper[hopper_pos] == None:
                self.hopper[hopper_pos] = QRCode2(0,largest.color,0) 
            else:
                self.hopper[hopper_pos].value = largest.color 
        else: 
            self.hopper[hopper_pos] = None
            print "no color found"
            return 0
            
    @lib.api_call 
    def check_box_color(self,Course):
        if Course == "right":
            Look = [85, 65, 170, 15, 180]
            self.rail.Orientor(1)
            self.joints = Look
            time.sleep(5)
            largest = self.GrabColor()
            self.joints = HOME
            time.sleep(5)
            self.reset_home_position()
            if largest != None:
                return largest.color 
            else:   
                return None
            
        if Course == "left":
            Look = [85,70,35,160,15,0]
            self.rail.Orientor(4)  
            time.sleep(1)
            self.joints = [85, 85,  20, 160, 0]
            time.sleep(8)
            largest = self.GrabColor()
            time.sleep(3)
            self.joints = HOME
            time.sleep(8)
            self.reset_home_position()
            time.sleep(1)
            if largest != None:
                return largest.color 
            else:
                return None
    
    @lib.api_call 
    def competition_solver_barge(self,Tier):
        
        i = 0
        while i< 2:
            Success = self.FindBlockWithIR(Tier)
            if Success:
                self.rail.DisplacementMover(-475)
                time.sleep(2)
                Position = self.rail.rail_motor.position
                
                self.Tier_Grab(Tier,1) 
                 
                time.sleep(2)
                self.rail.MoveToPosition(Position) 
                time.sleep(2) 
                self.Tier_Grab(Tier,2) 
                self.reset_home_position()
                
                i = i + 1
                self.reset_home_position() 
                
        return 1
        
            
            
            
            
    def test_partial_qr(self):
        self.cam.start()
        time.sleep(2)
        while True:
            time.sleep(.5)
            partial_list = self.cam.partial_qr_scan()
            ret = self.cam.partial_qr_select(partial_list)
            if ret != None:
                print "X = ", ret.tvec[0]
    
    @lib.api_call         
    def dd_solver(self):
        """
        Solver for design day. Lines uyp with a qrcode and grabs it and deposits it in the hopper
        """
        Tier = "B"
        i = 0
        while i< 2:
            self.rail.DisplacementConverter(3.5)
            Success = self.rail_feedback()
            if Success != None:
                #account for error
                self.rail.DisplacementMover(-900)
                time.sleep(2)
                Position = self.rail.rail_motor.position
                self.Tier_Grab(Tier,1) 
                time.sleep(2)
                self.rail.MoveToPosition(Position) 
                time.sleep(2) 
                self.Tier_Grab(Tier,2)
                i = i + 1
                self.reset_home_position() 
            else:
                print "No QRCode Found."
                return 0
        return 1
    @lib.api_call 
    def dd_check_bin(self, bin_id):
        """
        Looks at each bin position for the color of the bin
        saves data in self.bins
        
        self.bins order =>[left, back, right]
        """
        #TODO: Change values for checking the bins color on the back.
        CHECK_BIN_BACK = [0,80,25,160,2]
        self.reset_home_position()
        
        if bin_id == "left":
            color = self.check_box_color("right")       # yep, its reversed from the course orientation
            if color != None:
                self.bins[0] = color
                
        elif bin_id == "back":
            self.rail.DisplacementMover(3500)
            self.joints = CHECK_BIN_BACK
            time.sleep(8)
            largest = self.GrabColor()
            time.sleep(3)
            self.joints = HOME
            time.sleep(8)
            self.reset_home_position()
            time.sleep(1)
            if largest != None:
                self.bins[1] = largest.color

            
        elif bin_id == "right":
            color = self.check_box_color("left")        # yep, its reversed from the course orientation
            if color != None:
                self.bins[2] = color
        else:
            print "Unknown bin location given. Possible locations are 'left' 'back' and 'right'"
            
    @lib.api_call 
    def dd_empty_hopper(self):
        """
        Check the hopper items for a color match with a bin.
        If a match is found then it will deposit the block into that bin.
        """
        
        count = 0
        for block in self.hopper:
            count += 1
            if block == None:
                continue
            else:
                if block.value == self.bins[0]:
                    self.EmptyHopper(count, "right")
                    
                elif block.value == self.bins[1]:
                    Hopper = [0,85,170,20,180]
                    PullBack = [0,35,170,30,180]
                    #TODO Correct angles for dropping block off back
                    OffSide = [0,90,60,160,2]
                    self.reset_home_position()
                    self.rail.Orientor(count)
                    time.sleep(1)
                    self.servo_cape.transmit_block([0] + Hopper)
                    time.sleep(3)
                    self.grab() 
                    time.sleep(5)
                    self.joints = HOME 
                    time.sleep(5)
                    self.servo_cape.transmit_block([0] + OffSide)
                    self.rail.DisplacementMover(3500)
                    time.sleep(5)
                    self.release()
                    time.sleep(2)
                    self.joints = HOME
                    time.sleep(5)
                    self.reset_home_position()
                    time.sleep(8)
                    self.hopper[count - 1] = None
                    
                elif block.value == self.bins[2]:
                    self.EmptyHopper(count, "left")
                else:
                    print "No match for color -> bin."
    
    @lib.api_call 
    def check_hopper(self):
        i = 0
        while i < 4:
            print i 
            self.check_block_color(i) 
            i = i + 1
        return 1 
        
    @lib.api_call
    def orient(self, pos):
        self.rail.Orientor(pos)
    
    @lib.api_call
    def GrabQR(self):
        self.cam.start()
        time.sleep(2)
        QRcode = self.cam.QRSweep()
        self.cam.stop()
        return QRCode
        
    @lib.api_call
    def GrabColor(self):
        self.cam.start()
        self.TurnOnLight()
        time.sleep(2)
        ret = self.cam.check_color()
        if ret == None:         #try again
            print "Trying again"
            ret = self.cam.check_color()
            if ret == None:
                print "No color found. Assuming green."
                ret = Block(0, "green")
        self.TurnOffLight()
        self.cam.stop()
        return ret
        
    @lib.api_call
    def color_test_loop(self, hopper_pos):
        """
        Takes the hopper posisiton 0-3 as input and will look at the hopper posistion
        to see what clor it is then update the hopper array with the new data.
        
        this function loops to test how color detection works with different lighting conditions
        """
        HOPPER_LOOK = [0,75,140,10,180]
        #look at the hopper physically
        self.rail.Orientor(hopper_pos + 1)
        self.joints = HOPPER_LOOK
        time.sleep(3)
        while True:
            #look for a color
            largest = self.GrabColor()
            #udate with color found
            if largest != None:
                print "Color Found: ", largest.color
                if self.hopper[hopper_pos] != None:
                    self.hopper[hopper_pos] = QRCode2(0,largest.color,0)
                else:
                    #self.hopper[hopper_pos].value = largest.color
                    continue
            else: 
                print "Error: No color Found."
    
    @lib.api_call
    def TurnOnLight(self):
        self.servo_cape_grabber.transmit_block([3] + JUNK_BUFFER)
        
    @lib.api_call 
    def TurnOffLight(self):
        self.servo_cape_grabber.transmit_block([4] + JUNK_BUFFER) 
        
    @lib.api_call
    def FindBlockWithIR(self,Tier):
        
        if Tier == 'A':
            Look = [0,85,125,15,180]
            Threshold = 150
            NegativeThreshold = 200
        if Tier == 'B':
            Look = [0,75,125,20,180]
            Threshold = 80
            NegativeThreshold = 200
        
        
        
        
        self.joints = Look 
        time.sleep(3)
        
        
        
        self.rail.SetMotorPower()
        Value = self.IR.read_values()
        while Value["Arm"]>Threshold:
            
            if(self.rail.rail_motor.position > 6800): 
                self.orient(1)
                return 0
                
            #self.rail.DisplacementMover(75)
            #time.sleep(.25)
            Value = self.IR.read_values()
            print Value["Arm"] 
       
        while Value["Arm"]< NegativeThreshold: 
            
            if(self.rail.rail_motor.position > 6800): 
                self.orient(1)
                return 0
            #self.rail.DisplacementMover(75) 
            #time.sleep(.25)
            Value = self.IR.read_values()
        
        self.rail.StopMotor() 
        
       
        print Value["Arm"]
        return 1
        
    
