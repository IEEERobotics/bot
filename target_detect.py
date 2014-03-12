
#################################################################################################################
 Target_detect.py
# Authored by Rahul Krishna. Updated 3-11-14.
# Workes with Micrsoft lifecam VX-5000.
# Detects all the squares in the image, retruns the pixel location of the edges of the square. 
# It opens a window to display the detected target, this part is commented by default.
#################################################################################################################


import cv2
import cv
import numpy as np

# DEFINE CAMERA PARAMETERS

CV_CAP_PROP_POS_MSEC = 0
CV_CAP_PROP_POS_FRAMES = 1
CV_CAP_PROP_POS_AVI_RATIO = 2
CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4
CV_CAP_PROP_FPS = 5
CV_CAP_PROP_POS_FOURCC = 6
CV_CAP_PROP_POS_FRAME_COUNT = 7
CV_CAP_PROP_BRIGHTNESS = 8
CV_CAP_PROP_CONTRAST = 9
CV_CAP_PROP_SATURATION = 10
CV_CAP_PROP_HUE = 11
CV_CAP_PROP_AUTO_EXPOSURE = 12

CV_CAPTURE_PROPERTIES = tuple({
CV_CAP_PROP_POS_MSEC,
CV_CAP_PROP_POS_FRAMES,
CV_CAP_PROP_POS_AVI_RATIO,
CV_CAP_PROP_FRAME_WIDTH,
CV_CAP_PROP_FRAME_HEIGHT,
CV_CAP_PROP_FPS,
CV_CAP_PROP_POS_FOURCC,
CV_CAP_PROP_POS_FRAME_COUNT,
CV_CAP_PROP_BRIGHTNESS,
CV_CAP_PROP_CONTRAST,
CV_CAP_PROP_SATURATION,
CV_CAP_PROP_HUE,
CV_CAP_PROP_AUTO_EXPOSURE})

CV_CAPTURE_PROPERTIES_NAMES = [
"CV_CAP_PROP_POS_MSEC",
"CV_CAP_PROP_POS_FRAMES",
"CV_CAP_PROP_POS_AVI_RATIO",
"CV_CAP_PROP_FRAME_WIDTH",
"CV_CAP_PROP_FRAME_HEIGHT",
"CV_CAP_PROP_FPS",
"CV_CAP_PROP_POS_FOURCC",
"CV_CAP_PROP_POS_FRAME_COUNT",
"CV_CAP_PROP_BRIGHTNESS",
"CV_CAP_PROP_CONTRAST",
"CV_CAP_PROP_SATURATION",
"CV_CAP_PROP_HUE",
"CV_CAP_PROP_AUTO_EXPOSURE"]

capture = cv.CaptureFromCAM(0)

# SET CAMERA PARAMETERS, default image size is 320x240

cv.SetCaptureProperty(capture, CV_CAP_PROP_FRAME_WIDTH, 320)
cv.SetCaptureProperty(capture, CV_CAP_PROP_FRAME_HEIGHT, 240)
cv.SetCaptureProperty(capture, CV_CAP_PROP_AUTO_EXPOSURE, 5.0)


#################################################################################################################

# SOME FUNCTION DEFINITIONS FOR SQUARE DETECTION

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_squares(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv2.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
    return squares

#################################################################################################################
# MAIN LOOP

while True:

	im = cv.QueryFrame(capture) # Get frame
  col_edge = cv.CreateImage((im.width, im.height), 8, 3)
	dst = cv.CreateImage(cv.GetSize(im), 8, 1)
	color_dst = cv.CreateImage(cv.GetSize(im), 8, 3)
	storage = cv.CreateMemStorage(0)
# convert to grayscale
	gray = cv.CreateImage((im.width, im.height), 8, 1)
	edge = cv.CreateImage((im.width, im.height), 8, 1)
	hsv = cv2.cvtColor(np.asarray(im[:,:]), cv2.COLOR_BGR2HSV)

# Define range of Red color in HSV
# working Range [0 64 55], [24 255 255] and [163 64 55] [179 255 255]
# See wiki to see what the values mean. Basically, changing the first element changes the RED limit

# If the red values look unsatisfactory, there are two thing you could do:
# 1. Extend RED range.
# Increase the value of the first element in the 'upper_red' array (the default is 12)or(and) 
# decrease the value of the first element in the 'lower_red1'. 
# 2. To compesate for lighting effect, decrease the last element of lower_red and lower_red1 array.    	

    	lower_red = np.array([0,64,55])
    	upper_red = np.array([12,255,255])
	
	    lower_red1 = np.array([169,64,55])
    	upper_red1 = np.array([179,255,255])
	
# Threshold the image to get only Red color
  mask1 = cv2.inRange(hsv, lower_red, upper_red)
	mask2 = cv2.inRange(hsv, lower_red1, upper_red1)

# Perform an OR operation to get the FINAL MASK.
	mask = np.bitwise_or(mask1, mask2);
	
# Bitwise-AND mask and original image to extract the target.
	res = cv2.bitwise_and(np.asarray(im[:,:]),np.asarray(im[:,:]), mask= np.asarray(mask[:,:]))
	
# Square is the array that has the pixel values of the vertices, this is what we need. 
	squares=find_squares(res);
	


# The following section of the code is used to display the image. I am commenting them out.
#	cv2.drawContours(res, squares, -1, (0, 255, 0), 3 )
#  cv2.imshow('squares', res)
#	print squares
#	if cv.WaitKey(10) == 27:
#        	break
#	cv2.imshow('squares', res)


#################################################################################################################
