"""Encapsulates functionality of moving around robot arm"""

import simpy
﻿import sympy
import bot.lib.lib as lib
from bot.hardware.servo import Servo
from calcFKposition import *


class RobotArm(object):

   """An object that resembles a robotic arm with n joints"""
    def __init__(self, servo_assignments):

        for pwm in servo_assignments:

            self.joint_servos.append(Servo(pwm)) 
            
    
    @lib.api_call
    def set_joint_angle(self, joint, angle):
        """Sets the angle of an individual joint

        :param joint: Number of the joint (lowest joint being 1)
        :type joint: int
        :param angle: angle to be set (in degrees)
        :type angle: int
        """

        self.joint_servos[joint].position = angle 

    def calcFKposition(theta1, theta2, theta3, theta4, theta5, L1, L2, L3, L4, L5, L6):
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

    def InverseKinematic(targetX, targetY, targetZ):
        """ This function takes the current position of the arm (assumed at 180*)
            and a desired coordinate for the arm and outputs the angles of the servo's 
            
            :param targetX: target x value for the arm
            :type targetX: double
            :param targetY: target y value for the arm
            :type targetY: double
            :param targetZ: target z value for the arm
            :type targetZ: double
        
            Returns array of joint angles
    """

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
        T1 = a1
        T2 = a1 * a2
        T3 = a1 * a2 * a3
        T4 = a1 * a2 * a3 * a4
        T5 = a1 * a2 * a3 * a4 * a5
        T6 = a1 * a2 * a3 * a4 * a5 * a6

        # Extract Expressions for X, Y, Z coordinates
        Px = T[0, 3]
        Py = T[1, 3]
        Pz = T[2, 3]
        # print Px
        # print Py
        # print Pz

        # Calculate the Jacobian
        Pxyz = Matrix([Px, Py, Pz])
        the12345 = Matrix([the1, the2, the3, the4, the5])
        J = Pxyz.jacobian(the12345)

        # Prompt user for input
        #theA = (input("What is the A theta Value: ")) * (pi / 180)
        #theB = (input("What is the B theta Value: ")) * (pi / 180)
        #theC = (90 - input("What is the C theta Value: ")) * (pi / 180)
        #theD = (input("What is the D theta Value: ") - 90) * (pi / 180)
        
        theA = 180*(pi / 180)
        theB = 180*(pi / 180)
        theC = 180*(pi / 180)
        theD = 180*(pi / 180)
        theE = 90 *(pi / 180)

        # Create a vector of current joint angles
        Theta_cur = Matrix([[theA], [theB], [theC], [theD], [theE]])

        # Calculate the T matrices, based on current angles
        T1_cur = T1.subs(the1, theA)
        T1_cur = T1_cur.subs(the2, theB)
        T1_cur = T1_cur.subs(the3, theC)
        T1_cur = T1_cur.subs(the4, theD)
        T1_cur = T1_cur.subs(the5, theE)

        T2_cur = T2.subs(the1, theA)
        T2_cur = T2_cur.subs(the2, theB)
        T2_cur = T2_cur.subs(the3, theC)
        T2_cur = T2_cur.subs(the4, theD)
        T2_cur = T2_cur.subs(the5, theE)

        T3_cur = T3.subs(the1, theA)
        T3_cur = T3_cur.subs(the2, theB)
        T3_cur = T3_cur.subs(the3, theC)
        T3_cur = T3_cur.subs(the4, theD)
        T3_cur = T3_cur.subs(the5, theE)

        T4_cur = T4.subs(the1, theA)
        T4_cur = T4_cur.subs(the2, theB)
        T4_cur = T4_cur.subs(the3, theC)
        T4_cur = T4_cur.subs(the4, theD)
        T4_cur = T4_cur.subs(the5, theE)

        T5_cur = T5.subs(the1, theA)
        T5_cur = T5_cur.subs(the2, theB)
        T5_cur = T5_cur.subs(the3, theC)
        T5_cur = T5_cur.subs(the4, theD)
        T5_cur = T5_cur.subs(the5, theE)

        T6_cur = T6.subs(the1, theA)
        T6_cur = T6_cur.subs(the2, theB)
        T6_cur = T6_cur.subs(the3, theC)
        T6_cur = T6_cur.subs(the4, theD)
        T6_cur = T6_cur.subs(the5, theE)

        # Determine the current position using forward kinematics
        # print theA, theB, theC, theD, theE, l1, l2, l3, l4, l5, l6
        [x_cur, y_cur, z_cur] = calcFKposition(
            theA, theB, theC, theD, theE, l1, l2, l3, l4, l5, l6)
        #print x_cur
        #print y_cur
        #print z_cur

        #---Inverse Kinematics---
        # Get user input for new target coordinates, X,Y,Z
        #x_goal = input("What is the target X Value: ")
        #y_goal = input("What is the target Y Value: ")
        #z_goal = input("What is the target Z Value: ")

        x_goal = targetX
        y_goal = targetY
        z_goal = targetZ

        goal = Matrix([x_goal, y_goal, z_goal])
        cur = Matrix([x_cur, y_cur, z_cur])
        displacement = (goal - cur)

        #print 'Displacement Distance'
        dist = displacement.norm()
        #print dist

        J_cur = J.subs(the1, theA)
        J_cur = J_cur.subs(the2, theB)
        J_cur = J_cur.subs(the3, theC)
        J_cur = J_cur.subs(the4, theD)
        J_cur = J_cur.subs(the5, theE)

        #print J_cur

        J_inv = J_cur.pinv()
        #print 'Jacobian Pseudoinverse at Current Position '
        #print J_inv

        Theta_next = (Theta_cur + J_inv * displacement)
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

            T1_cur = T1.subs(the1, theA)
            T1_cur = T1_cur.subs(the2, theB)
            T1_cur = T1_cur.subs(the3, theC)
            T1_cur = T1_cur.subs(the4, theD)
            T1_cur = T1_cur.subs(the5, theE)

            T2_cur = T2.subs(the1, theA)
            T2_cur = T2_cur.subs(the2, theB)
            T2_cur = T2_cur.subs(the3, theC)
            T2_cur = T2_cur.subs(the4, theD)
            T2_cur = T2_cur.subs(the5, theE)

            T3_cur = T3.subs(the1, theA)
            T3_cur = T3_cur.subs(the2, theB)
            T3_cur = T3_cur.subs(the3, theC)
            T3_cur = T3_cur.subs(the4, theD)
            T3_cur = T3_cur.subs(the5, theE)

            T4_cur = T4.subs(the1, theA)
            T4_cur = T4_cur.subs(the2, theB)
            T4_cur = T4_cur.subs(the3, theC)
            T4_cur = T4_cur.subs(the4, theD)
            T4_cur = T4_cur.subs(the5, theE)

            T5_cur = T5.subs(the1, theA)
            T5_cur = T5_cur.subs(the2, theB)
            T5_cur = T5_cur.subs(the3, theC)
            T5_cur = T5_cur.subs(the4, theD)
            T5_cur = T5_cur.subs(the5, theE)

            T6_cur = T6.subs(the1, theA)
            T6_cur = T6_cur.subs(the2, theB)
            T6_cur = T6_cur.subs(the3, theC)
            T6_cur = T6_cur.subs(the4, theD)
            T6_cur = T6_cur.subs(the5, theE)

            [x_cur, y_cur, z_cur] = calcFKposition(
                theA, theB, theC, theD, theE, l1, l2, l3, l4, l5, l6)
		
            cur = Matrix([x_cur, y_cur, z_cur])
            displacement = (goal - cur)
            #print 'Displacement Distance'
            dist = displacement.norm()
            #print dist

            J_cur = J.subs(the1, theA)
            J_cur = J_cur.subs(the2, theB)
            J_cur = J_cur.subs(the3, theC)
            J_cur = J_cur.subs(the4, theD)
            J_cur = J_cur.subs(the5, theE)

            J_inv = J_cur.pinv()
            #print 'Jacobian Pseudoinverse at Current Position '
            #print J_inv

            Theta_next = (Theta_cur1 + J_inv * displacement)
            #print 'Next Joint Angles'
            #print Theta_next
            #print "X = " + x_cur
            #print "X = " + y_cur
            #print "X = " + z_cur
            

        ThetaArray = [Theta_next[0],Theta_next[1], Theta_next[2], Theta_next[3], Theta_next[4]]
        return ThetaArray


