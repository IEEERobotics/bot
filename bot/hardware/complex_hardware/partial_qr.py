from math import sqrt
import cv2
import numpy as np

def find_center(cnt):
    (x,y), r = cv2.minEnclosingCircle(cnt)
    center = (int(x), int(y))
    return center

def distance(a, b):
    return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def same_qr(marker1, marker2):
    """Checks to see if markers are on same qr.
    """
    
    dist = distance(marker1.center, marker2.center)     
    height = float(max([marker1.height, marker2.height]))
    width  = float(max([marker1.width, marker2.width]))

    dx = abs(marker1.x - marker2.x) 
    dy = abs(marker1.y - marker2.y)
    
    vert_upper_range  = 1.5 <= float(abs(dy/height )) <= 2.5
    horiz_upper_range = 1.5 <= float(abs(dx/width )) <= 2.5
    
    vert_lower_range = 0 <= float(abs(dy/height )) <= .5
    horiz_lower_range = 0 <= float(abs(dx/width )) <= .5
    
    
    #truth table:
    if (vert_upper_range and horiz_lower_range):
        return True
    elif (horiz_upper_range and vert_lower_range):
        return True
    elif (horiz_upper_range and vert_upper_range):
        return True
    else:
        return False

#idk if we should use this
class Marker(object):
    def __init__(self, contour):
        peri = cv2.arcLength(contour, True)
        self.contour = contour
        #co-ords based on center of marker
        self.center = find_center(contour)

        self.x = self.center[0]
        self.y = self.center[1]
        

        self.approx = cv2.approxPolyDP(contour, 0.02*peri, True)

        #optimize
        (rx, ry, w, h) = cv2.boundingRect(self.approx) 
        self.width = w
        self.height = h
        self.length = (w + h)/2

class PartialQR(object):
    
    def __init__(self, a, b, c):
        self.marker1 = a
        self.marker2 = b
        self.marker3 = c


def find_markers(contours, hierarchy):
    #technique borrowed form dysnflow
    # find contours with 3 children
    marker_list = []
    for i in range(len(contours)):
        k = i
        children = 0

        # Iterate until pointing to a contour with no children
        while hierarchy[0][k][2] != -1:
            k = hierarchy[0][k][2]
            children += 1
 
        if children > 3 or (children >= 1 and is_square(contours[i])):

            #castrate all children
            j = i
            while hierarchy[0][j][2] != -1:
                buff = j
                #point to next child
                j = hierarchy[0][j][2] 
                # castrate current child
                hierarchy[0][buff][2] = -1
            # find highest parent, castrate along the way.
            j = i
            while hierarchy[0][j][3] != -1:
                hierarchy[0][j][2] = -1
                j = hierarchy[0][j][3]

            marker_list.append(Marker(contours[j]))
    return marker_list


def is_square(contour):

    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02*peri, True)
    #if contour has 4 points, 
    if len(approx) >= 4 and len(approx) <= 6:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspectRatio = w/ float(h)


        # find areas
        area = cv2.contourArea(contour)
        hullArea = cv2.contourArea(cv2.convexHull(contour))

        solidity = area / float(hullArea)

        keepSolidity = solidity > 0.9
        keepAspectRatio = (aspectRatio >= 0.8 and aspectRatio <= 1.2 )

        keepSize = cv2.arcLength(contour, True) > 60

        # Check that it has children. (-1 if none)
        # form: [next, previous, child, parent]

        if keepSolidity and keepAspectRatio and keepSize:
            return True
        else:
            return False

def largest_edge(mark):
    if (mark.width > mark.height):
        return mark.width
    else:
        return mark.height
    

def find_matching_marker(marker, marker_list):
    """finds all markers in the same list."""
    
    m_list = list(marker_list)
    
    
    m_list.remove(marker)
    
    #matches = [m for m in m_list if same_qr(marker, m)]
    matches = []
    for m in m_list:
        if same_qr(marker, m):
            matches.append(m)
    
    return matches

def partial_center(pqr):
    #find average length
    avg_length = int((pqr.marker1.length + pqr.marker2.length + pqr.marker3.length)/3)
    if abs(pqr.marker1.x -pqr.marker2.x) >= (1.5 * avg_length):
        center_x = int((pqr.marker1.x + pqr.marker2.x)/2)
    elif abs(pqr.marker1.x -pqr.marker3.x) >= (1.5 * avg_length):
        center_x = int((pqr.marker1.x + pqr.marker3.x)/2)
    elif abs(pqr.marker2.x -pqr.marker3.x) >= (1.5 * avg_length):
        center_x = int((pqr.marker2.x + pqr.marker3.x)/2)
    else:
        center_x = int((pqr.marker1.x + pqr.marker2.x + pqr.marker3.x)/2)
        
    if abs(pqr.marker1.y -pqr.marker2.y) >= (1.5 * avg_length):
        center_y = int((pqr.marker1.y + pqr.marker2.y)/2)
    elif abs(pqr.marker1.y -pqr.marker3.y) >= (1.5 * avg_length):
        center_y = int((pqr.marker1.y + pqr.marker3.y)/2)
    elif abs(pqr.marker2.y -pqr.marker3.y) >= (1.5 * avg_length):
        center_y = int((pqr.marker2.y + pqr.marker3.y)/2)
    else:
        center_y = int((pqr.marker1.y + pqr.marker2.y + pqr.marker3.y)/2)
        
    return center_x, center_y

