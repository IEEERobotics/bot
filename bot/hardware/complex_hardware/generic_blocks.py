import cv2
import numpy as np
import sys
import os
from math import sin,cos,pi,copysign,tan,sqrt,hypot

AREA_THRESHOLD=500

FOV=47

BLOCK=1.5 


#Finds the blocks
def internal_find_blocks(img):
    hsv = cv2.cvtColor(img, cv2.cv.CV_BGR2HSV)

    hsv[:,:,1] = 255
    hsv[:,:,2] = 255

    
    hsv=cv2.cvtColor(hsv, cv2.cv.CV_HSV2BGR)
    

    for i in range(5):
        hsv = cv2.GaussianBlur(hsv,(3,3),0)

    hsv = cv2.inRange(hsv, (220,0,0), (255,255,255))
    
    contours = cv2.findContours(hsv, cv2.cv.CV_RETR_LIST, cv2.cv.CV_CHAIN_APPROX_SIMPLE)

    result=[]

    

    for c in contours[0]:

        if cv2.contourArea(c)>AREA_THRESHOLD:
            epsilon = 0.01*cv2.arcLength(c,True)
            approx = cv2.approxPolyDP(c,epsilon,True)
            rect = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            ratio=cv2.contourArea(approx)/cv2.contourArea(box)
            if 1:#ratio>.75:    #THIS IS TO FILTER OUT BAD PARTICLES Not in use.
                rect = cv2.minAreaRect(box)
            elif ratio>.25:
                continue


            
            result.append(rect)
    return result

#Does math on the blocks
def block_math(rect, img, actual_dist=0, centered=False):
    cx=rect[0][0]
    cy=rect[0][1]
    thetad=rect[2]
    theta=thetad/360*2*pi
    w=rect[1][0]/2.0
    h=rect[1][1]/2.0
    if abs(thetad)>45:
        temp=h
        h=w
        w=temp
        theta-=pi/2
        thetad-=90
    thetad+=90
    thetad=copysign(90,thetad)-thetad
    imgh,imgw,_=np.shape(img)
    w*=2
    h*=2

    if cx-w/2<10 or cx+w/2>imgw-10:return None

    rpp = pi/180*FOV/imgw
    
    dist = 1.5/2/tan(w*FOV*pi/180/imgw/2)

    if centered:actual_dist=dist
    
    if cx < imgw/2:
        hoffset = actual_dist * tan((cx-w/2-imgw/2)*rpp) + BLOCK/2
    else:
        hoffset = actual_dist * tan((cx+w/2-imgw/2)*rpp) - BLOCK/2

    if cy < imgh/2:
        voffset = actual_dist * tan((cy-h/2-imgh/2)*rpp) + BLOCK/2
    else:
        voffset = actual_dist * tan((cy+h/2-imgh/2)*rpp) - BLOCK/2
    
    return hoffset,-voffset,dist


#Returns a list of the lateral offsets for each block found. (inches)
#You probably want the one closest to 0.
#Call this first and then compensate
#Assume distance should be what is reported by the IR/distance sensors in inches
def get_lateral_offset(img,assume_dist):
    blocks=internal_find_blocks(img)
    if len(blocks)==0:return -1

    results=[]
    
    for rect in blocks:          
        coords=block_math(rect,img,assume_dist)
        if coords is not None:results.append(coords[0])
    #return x offset of blocks
    results=sorted(results)
    return results

#Returns coordinates for each block found.
#Again, probably want the one closest to 0.
#Call get_lateral_offset first and center.
# format (dx,dy,dz) in inches from where the arm is now.
def get_front_center(img):
    blocks=internal_find_blocks(img)
    if len(blocks)==0:return -1

    results=[]
    
    for rect in blocks:
        coords=block_math(rect,img,centered=True)
        if coords is not None:results.append(coords)

    results=sorted(results, key=lambda x: abs(x[0]))

    return results
    #return location vectors

    


            
