import generic_blocks
import cv2 
import sys
import os
import numpy as np

cam = cv2.VideoCapture(0)
cam.set(3, 632)#320)
cam.set(4, 474)#240)
print cam.get(3)
print cam.get(4)
actual_dist=10.25 #sensor value here


try:
    while 1:
	print 'hi1'
	cam.grab()
	cam.grab()
	cam.grab()
	cam.grab()
        ret,img=cam.read()
	img = np.array(img)
	print 'hi2'
        print 'Horiz:',generic_blocks.get_lateral_offset(img,actual_dist)
        raw_input()
        print 'Coords:',generic_blocks.get_front_center(img)
        raw_input()
#        print generic_blocks.internal_find_blocks(img)
        
        #cv2.imshow('hi',img)
        #cv2.waitKey(1)
except Exception as e:
    print sys.exc_info()
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
cam.release()
