"""Encapsulates functionality of moving around robot arm"""

import sympy
from sympy import *
import bot.lib.lib as lib
from bot.hardware.servo_cape import ServoCape


class RobotArm(object):


    """An object that resembles a robotic arm with n joints"""
    def __init__(self, arm_config):
        
        self.default_angles = [90]*5
        self.logger = lib.get_logger()
        self.bot_config = lib.get_config()
        
        self.servo_cape \
            = ServoCape(self.bot_config["dagu_arm"]["servo_cape"])     
        # Empty list of zeros representing each joint   
        self.joints = [0]*5
        
    @lib.api_call
    def grab(self):
        self.servo_cape.transmit_block([5] + [0,0,0,0,0])
        
    @lib.api_call   
    def release(self):
        self.servo_cape.transmit_block([6] + [0,0,0,0,0])
        
    @lib.api_call
    def set_angles(self):
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
            answer = input("Do you want to send these angles?(y/n)")
            if (answer is "n"):
                return
            elif (answer is "y"):
                array = [A1,A2,A3,A4,A5]
                self.servo_cape.transmit_block([0] + array)
                return
            else:
                print "Error: Invalid reply. Please answer in y/n format."
        
        
        
    @lib.api_call
    def reset_home_position(self):
        """sets angles back to default position."""
        self.servo_cape.transmit_block([0] + [90,90,90,90,90])
        
    @lib.api_call
    def Arm_Demo(self):
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
                                         + [0]*5)        
    

    def calcFKposition(self, theta1, theta2, theta3, theta4, theta5, L1, L2, L3, L4, L5, L6):
        """ Finds the current xyz given the lengths and theta values

        :param thetaX:  angle of joint x
        :type thetaX:   double
        :param LX:      length of arm x
        :type LX:       double

        :returns: 3x1 matrix of xyz location

        """

        Px = ((1 / 2.) * L2 * cos(theta1 - theta2) +
            (1 / 2.) * L2 * cos(theta1 + theta2) +
            -(1 / 2.) * L6 * sin(theta1 + theta5) +
            -(1 / 2.) * L6 * sin(theta1 - theta5) +
            (1 / 2.) * L3 * cos(-theta3 + theta1 - theta2) +
            (1 / 2.) * L3 * cos(theta3 + theta1 + theta2) +
            (1 / 2.) * L5 * cos(-theta4 - theta3 + theta1 - theta2) +
            (1 / 2.) * L5 * cos(theta4 + theta3 + theta1 + theta2) +
            (1 / 2.) * L4 * cos(theta4 + theta3 + theta1 + theta2) +
            (1 / 2.) * L4 * cos(-theta4 - theta3 + theta1 - theta2) +
            (1 / 4.) * L6 * cos(theta1 + theta2 + theta3 + theta5 + theta4) +
            (1 / 4.) * L6 * cos(theta1 - theta2 - theta3 - theta5 - theta4) +
            -(1 / 4.) * L6 * cos(theta1 + theta2 + theta3 - theta5 + theta4) +
            -(1 / 4.) * L6 * cos(theta1 - theta2 - theta3 + theta5 - theta4))

        Py = ((1 / 2.) * L6 * cos(theta1 - theta5) +
            (1 / 2.) * L6 * cos(theta1 + theta5) +
            (1 / 2.) * L2 * sin(theta1 + theta2) +
            (1 / 2.) * L2 * sin(theta1 - theta2) +
            (1 / 2.) * L3 * sin(theta3 + theta1 + theta2) +
            (1 / 2.) * L3 * sin(-theta3 + theta1 - theta2) +
            (1 / 2.) * L5 * sin(theta4 + theta3 + theta1 + theta2) +
            (1 / 2.) * L5 * sin(-theta4 - theta3 + theta1 - theta2) +
            (1 / 2.) * L4 * sin(theta4 + theta3 + theta1 + theta2) +
            (1 / 2.) * L4 * sin(-theta4 - theta3 + theta1 - theta2) +
            (1 / 4.) * L6 * sin(theta1 - theta2 - theta3 - theta5 - theta4) +
            (1 / 4.) * L6 * sin(theta1 + theta2 + theta3 + theta5 + theta4) +
            -(1 / 4.) * L6 * sin(theta1 - theta2 - theta3 + theta5 - theta4) +
            -(1 / 4.) * L6 * sin(theta1 + theta2 + theta3 - theta5 + theta4))

        Pz = (L3 * sin(theta2 + theta3) +
            L5 * sin(theta2 + theta4 + theta3) +
            L4 * sin(theta2 + theta4 + theta3) +
            (1 / 2.) * L6 * sin(theta5 + theta4 + theta2 + theta3) +
            -(1 / 2.) * L6 * sin(-theta5 + theta4 + theta2 + theta3) +
            L2 * sin(theta2) +
            L1)

        P = Matrix([Px, Py, Pz])
        return P

    @lib.api_call
    def InverseKinematics(self, X_goal,Y_goal, Z_goal):

    	""" This function takes the current position of the arm (assumed at 180*)
	        and a desired coordinate for the arm and outputs the angles of the serv$
	        :param targetX: target x value for the arm
	        :type targetX: double
	        :param targetY: target y value for the arm
	        :type targetY: double
	        :param targetZ: target z value for the arm
	        :type targetZ: double
	    
	        Returns array of joint angles
    	"""

        #print("Inverse Kinematic Start")
        # Symbolic Setup
        the, a, d, al, b, l1, l2, l3, l4, l5 = symbols(
            "the a d al b l1 l2 l3 l4 l5")
        the1, the2, the3, the4, the5 = symbols("the1 the2 the3 the4 the5")
    
        # Kinematic Constants and Symbols
        pi = sympy.pi
        b = 5.5
        l1 = 9
        l2 = 8
        l3 = 8.1
        l4 = 4.8
        l5 = 5.7
        l6 = 9
        s1 = sin(the)
        c1 = cos(the)
        s2 = sin(al)
        c2 = cos(al)
        
        theA = 45 * (pi / 180)
        theB = 45 * (pi / 180)
        theC = (90-45) * (pi / 180)
        theD = (45-90) * (pi / 180)
        theE = 90 * (pi / 180)
        
        Theta_cur = Matrix([[theA], [theB], [theC], [theD], [theE]])
        
        [x_cur, y_cur, z_cur] = self.calcFKposition(
            theA, theB, theC, theD, theE, l1, l2, l3, l4, l5, l6)
        
        x_cur = x_cur.evalf(5)
        y_cur = y_cur.evalf(5)
        z_cur = z_cur.evalf(5)
        
        #print "Forward Kinematics Position"
        #print x_cur
        #print y_cur
        #print z_cur
    
        # Coordinate Transforms
        A = Matrix(
            [[c1, -s1 * c2, s1 * s2, a * c1], [s1, c1 * c2, -c1 * s2, a * s1], [0, s2, c2, d], [0, 0, 0, 1]])
    
        a1 = A.subs(the, the1)
        a1 = a1.subs(d, b + l1)
        a1 = a1.subs(a, 0)
        a1 = a1.subs(al, pi / 2)
    
        a2 = A.subs(the, the2)
        a2 = a2.subs(d, 0)
        a2 = a2.subs(a, l2)
        a2 = a2.subs(al, 0)
    
        a3 = A.subs(the, the3)
        a3 = a3.subs(d, 0)
        a3 = a3.subs(a, l3)
        a3 = a3.subs(al, 0)
    
        a4 = A.subs(the, the4)
        a4 = a4.subs(d, 0)
        a4 = a4.subs(a, l4)
        a4 = a4.subs(al, pi / 2)
    
        a5 = A.subs(the, -pi / 2)
        a5 = a5.subs(d, 0)
        a5 = a5.subs(a, 0)
        a5 = a5.subs(al, -pi / 2)
    
        a6 = A.subs(the, the5)
        a6 = a6.subs(d, l5)
        a6 = a6.subs(a, l6)
        a6 = a6.subs(al, -pi / 2)
    
        T = a1 * a2 * a3 * a4 * a5 * a6
        
        Px = T[0, 3]
        Py = T[1, 3]
        Pz = T[2, 3]   
        
        goal = Matrix([X_goal, Y_goal, Z_goal])
        cur = Matrix([x_cur, y_cur, z_cur])
        displacement = (goal - cur)
        
        dist = displacement.norm().evalf(5)
        #print dist
        
        Pxyz = Matrix([Px, Py, Pz])
        the12345 = Matrix([the1, the2, the3, the4, the5])
        J = Pxyz.jacobian(the12345)
        
        J_cur = J.subs(the1, theA)
        J_cur = J_cur.subs(the2, theB)
        J_cur = J_cur.subs(the3, theC)
        J_cur = J_cur.subs(the4, theD)
        J_cur = J_cur.subs(the5, theE)
        
        J_cur = J_cur.evalf(5)
        
        J_inv = J_cur.pinv()
        
        Theta_next = (Theta_cur + J_inv * displacement).evalf(5)
        #print 'Next Joint Angles'
        #print Theta_next
        
        while (dist > 1):
            #print '=============================================================='
    
            theA = Theta_next[0]
            theB = Theta_next[1]
            theC = Theta_next[2]
            theD = Theta_next[3]
            theE = pi / 2
            Theta_cur1 = Matrix([theA, theB, theC, theD, theE])
    
            [x_cur, y_cur, z_cur] = self.calcFKposition(
                theA, theB, theC, theD, theE, l1, l2, l3, l4, l5, l6)
    		
            #print "Forward Kinematics Position"
            #print x_cur.evalf(5)
            #print y_cur.evalf(5)
            #print z_cur.evalf(5)
            
            cur = Matrix([x_cur, y_cur, z_cur])
            displacement = (goal - cur)
            #print 'Displacement Distance'
            dist = displacement.norm().evalf(5)
            #print dist
    
            J_cur = J.subs(the1, theA)
            J_cur = J_cur.subs(the2, theB)
            J_cur = J_cur.subs(the3, theC)
            J_cur = J_cur.subs(the4, theD)
            J_cur = J_cur.subs(the5, theE)
            
            J_cur = J_cur.evalf(5)
            J_inv = J_cur.pinv().evalf(5)
    
            Theta_next = (Theta_cur1 + J_inv * displacement).evalf(5)
            #print 'Next Joint Angles'
            #print Theta_next
            #print '=============================================================='
            #print "X = " + x_cur
            #print "X = " + y_cur
            #print "X = " + z_cur
            
            
    
        #print "DONE"
        ThetaArray = [int((Theta_next[0]*180/pi).evalf()), int((Theta_next[1]*180/pi).evalf()), int((Theta_next[2]*180/pi).evalf()), int((Theta_next[3]*180/pi).evalf()), int((Theta_next[4]*180/pi).evalf())]
        self.servo_cape.write_angles(ThetaArray)


