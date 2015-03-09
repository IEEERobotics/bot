"""Preprocessing of IR sensor

W is the width of IR sensor array

L is the distance between the front and back sensor array

d is the distance between two IR sensor

N1 represents the first high reading value (from left to right) for front IR

N2 represents the first high reading value (from left to right) for back IR

n1 represents the relative coordinate for the front IR

n2 represents the relative coordinate for the back IR """

import sys

from time import time

class PID_data(object):

    def __init__(self,d,l,w):
        self.n1 = 0
        self.n2 = 0
        self.d  = d
        self.l = l
        self.w = w
        self.ttheta=0
        self.N1 = 0
        self.N2 = 0
#        self.theta = 0
#        self.s = 0

"""    def cal_value(self,N1,N2)
        self.n1 = N1-4.5
        self.n2 = N2-4.5
        self.ttheta = (self.n1-self.n2)*self.d/self.l
        
   
"""
    def IR_switch(self,a)
        self.N1[7] = a["front"][0]
        self.N1[6] = a["front"][1]
        self.N1[5] = a["front"][2]
        self.N1[4] = a["front"][3]
        self.N1[3] = a["front"][4]
        self.N1[2] = a["front"][5]
        self.N1[1] = a["front"][6]
        self.N1[0] = a["front"][7]

        self.N2[7] = a["back"][7]
        self.N2[6] = a["back"][6]
        self.N2[5] = a["back"][5]
        self.N2[4] = a["back"][4]
        self.N2[3] = a["back"][3]
        self.N2[2] = a["back"][2]
        self.N2[1] = a["back"][1]
        self.N2[0] = a["back"][0]        
        
    def IR_index(self,IR)
        i=0
#        if (sum[IR]>=2)
        if (IR[i]==0)
            i=i+1
        else (IR[i]=1)
            N=i
     
        
    def propa_error(self,N1,N2)
        self.n1 = self.N1-3.5
        self.n2 = self.N2-4.5
        self.ttheta = (self.n1-self.n2)*self.d/self.l
        theta = atan(self.ttheta)
        return theta
     
    def rotate_error(self,N1,N2)
        self.n1 = N1-4.5
        self.n2 = N2-4.5
        self.ttheta = (self.n1-self.n2)*self.d/self.l
        s = abs(-self.l*self.ttheta-self.n2)/((1+self.ttheta^2)^0.5)
        return s
        
        


