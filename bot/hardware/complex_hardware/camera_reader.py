
import numpy as np
import time

import zbar
import cv2
from PIL import Image
import cv2
import math


import bot.lib.lib as lib
from bot.hardware.qr_code import QRCode
from bot.hardware.complex_hardware.QRCode2 import QRCode2

class Camera(object):

    L = 1.5
    qr_verts = np.float32([[-L/2, -L/2, 0],
                            [-L/2,  L/2, 0],
                            [ L/2, -L/2, 0],
                            [ L/2,  L/2, 0]])

    def __init__(self, cam_config):
        # Recieves 

        self.logger = lib.get_logger()
        
        self.cam = cv2.VideoCapture(-1)
        self.cam.set(3, 632)
        self.cam.set(4, 474)
        
        self.resX = self.cam.get(3)
        self.resY = self.cam.get(4)

        # QR scanning tools
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')
        
        # Camera calibrations
        self.cam_matrix = np.float32(cam_config["camera_matrix"])
        self.dist_coeffs = np.float32(cam_config["distortion_coefficients"])
        
        L = 1.5
        self.qr_verts = np.float32([[-L/2, -L/2, 0],
                            [-L/2,  L/2, 0],
                            [ L/2, -L/2, 0],
                            [ L/2,  L/2, 0]])

    def apply_filters(self, frame):
        """Attempts to improve viewing by applying filters """
        # grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        santized_frame = cv2.bilateralFilter(thresh, 9, 75, 75) 
        return santized_frame

    @lib.api_call
    def get_current_frame(self):
        self.cam.grab()        
        self.cam.grab()        
        self.cam.grab()        
        self.cam.grab()       
        return self.cam.read()
 
    def get_zbar_im(self, qr_frame):
        cv2.imwrite('buffer.png', qr_frame)
        pil_im = Image.open('buffer.png').convert('L')
        width, height = pil_im.size
        raw = pil_im.tobytes()

        return zbar.Image(width, height, 'Y800', raw)

    @lib.api_call
    def get_qr_list(self, frame):
        """Recieves frame, assuming it's already been sanitizes, 
        and returns a list of all qr codes in it.
        """
 
        z_im = self.get_zbar_im(frame)
        self.scanner.scan(z_im)
        qr_list = []
        # Gather list of all QR objects
        for symbol in z_im:
            print "qr found"
            tl, bl, br, tr = [item for item in symbol.location]
            points = np.float32(np.float32(symbol.location))
            qr_list.append(QRCode(symbol, self.L))
        return qr_list
 
    @lib.api_call
    def sort_closest_qr(self, qr_list):
        """returns sortest list with closest qr first"""

        for code in qr_list:
            _, code.rvec, code.tvec = cv2.solvePnP(code.verts
                                               , code.points
                                               , self.cam_matrix
                                               , self.dist_coeffs)
            
        # Finds qr with smallest displacement 
        qr_list.sort(key=lambda qr: qr.displacement, reverse=False)
        return qr_list 

    @lib.api_call
    def get_target_qr(self):

        while True:
            ret, frame = self.get_current_frame()
            clean_frame = self.apply_filters(frame)
            z_im = self.get_zbar_im(clean_frame)
            qr_list = self.get_qr_list(z_im)
            sorted_qr = self.sort_closest_qr
            if sorted_qr != None:
                break

    def draw_qr_on_frame(self, frame, qr):
        cv2.line(frame, qr.topLeft, qr.topRight, (20, 20, 255), 8, 8)
        cv2.line(frame, qr.topRight, qr.bottomRight, (20, 20, 255), 8, 8)
        cv2.line(frame, qr.bottomRight, qr.bottomLeft, (20, 20, 255), 8, 8)
        cv2.line(frame, qr.bottomLeft, qr.topLeft, (20, 20, 255), 8, 8)
        return frame

    @lib.api_call 
    def infinite_demo(self):
        while True:
            ret, frame = self.get_current_frame()
            cv2.imshow('frm', frame)
            clean_frame = self.apply_filters(frame)

            found_qrs = self.get_qr_list(clean_frame)
  
            qr_frame = clean_frame
            for qr in found_qrs:
                qr_frame = self.draw_qr_on_frame(qr_frame, qr)
            cv2.imshow('qrs',  qr_frame) 
            print "found_qrs", found_qrs           
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if found_qrs == None or found_qrs == []:
                continue

            sorted_qr = self.sort_closest_qr(found_qrs)
            targetQR = sorted_qr[0]

        self.cam.release()
        cv2.destroyAllWindows

    @lib.api_call
    def QRSweep(self):
        
        QRList = []
        self.cam.grab()
        self.cam.grab()
        self.cam.grab()
        self.cam.grab()
        #cv2.waitKey(50)
        ret, frame = self.cam.read()   
        
        # Direct conversion cv -> zbar images did not work.
        # Buffer file used to have native data structures.

        # PIL -> zbar

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        ret, thresh = cv2.threshold(gray,85,255,cv2.THRESH_BINARY)
        cv2.imwrite('buffer.png', thresh)
        pil_im = Image.open('buffer.png').convert('L')

        width, height = pil_im.size
        raw = pil_im.tobytes()
        z_im = zbar.Image(width, height, 'Y800', raw)

        # Find codes in image
        self.scanner.scan(z_im)
        count = 0
        for symbol in z_im:
            tl, bl, br, tr = [item for item in symbol.location]
            points = np.float32([[tl[0], tl[1]],
                                 [tr[0], tr[1]],
                                 [bl[0], bl[1]],
                                 [br[0], br[1]]])

            tvec = self.solveQR(tl, tr, bl, br)

            print symbol.data
            print "X_Displacement = ", tvec[0]
            print "Y_Displacement = ", tvec[1]
            print "Z_Displacement = ", tvec[2]
            print "========================================="

            QRList.append(QRCode2(tvec, symbol.data, tr)) 
            count += 1

        if count == 0:
            print "No QRCode Found"
            return None
        
        targetQR = self.selectQR(QRList)
        if targetQR == None:
            print "No QRCode Found"
        else: 
            print "value: ", targetQR.value
            print "X:     ", targetQR.tvec[0]
            print "Y:     ", targetQR.tvec[1]
            print "X:     ", targetQR.tvec[2]
        #self.cam.release()
        return targetQR
    
    def selectQR(self, QRList):
        # find the best QRCode to grab (closest x then highest y)
        QRList.sort(key=lambda qr: qr.tvec[0], reverse=False)       # sort the list of qr codes by x, smallest to largest
        x_min = 100
        min_qr = 0
        count = 0
        for qr in QRList:
            #find smallest x
            if abs(qr.tvec[0]) < abs(x_min):
                x_min = qr.tvec[0]
                min_qr = count
            count += 1
        targetQR = None
        #check upper and lower qrs in list for height
        if (min_qr > 0):
            if (abs(QRList[min_qr -1].tvec[0] - x_min) < .1):
                if QRList[min_qr -1].tvec[1] < QRList[min_qr].tvec[1]:
                    targetQR = QRList[min_qr-1]
                else:
                    targetQR = QRList[min_qr]
        if ((min_qr < (len(QRList) - 1)) and (targetQR == None)):
            if (abs(QRList[min_qr +1].tvec[0] - x_min) < .1):
                if QRList[min_qr +1].tvec[1] < QRList[min_qr].tvec[1]:
                    targetQR = QRList[min_qr+1]
                else:
                    targetQR = QRList[min_qr]
        if targetQR == None:
            targetQR = QRList[min_qr]
            
        return targetQR
    
    
    #new solvepnp
    def solveQR(self, tl, tr, bl, br):
        QRSize = 1.5                # units = inches
        center = [self.resX/2, self.resY/2]

        #find the center of the QRCode
        QRCenter = [int((tl[0] + tr[0] + bl[0] + br[0])/4), int((tl[1] + tr[1] + bl[1] + br[1])/4)]

        #find pixel displacement
        pixel_displacement = [(QRCenter[0] - center[0]),(QRCenter[1] - center[1])]

        #find Z distance to QRCode
        north = int(math.sqrt(pow(abs(tl[0] - tr[0]), 2) + pow(abs(tl[1] - tr[1]), 2)))
        south = int(math.sqrt(pow(abs(bl[0] - br[0]), 2) + pow(abs(bl[1] - br[1]), 2)))
        east = int(math.sqrt(pow(abs(tr[0] - br[0]), 2) + pow(abs(tr[1] - br[1]), 2)))
        west = int(math.sqrt(pow(abs(tl[0] - bl[0]), 2) + pow(abs(tl[1] - bl[1]), 2)))

        if (north >= south and north >= east and north >= west):
            largest_edge = north
        elif (south >= east and south >= west):
            largest_edge = south
        elif (east >= west):
            largest_edge = east
        else:
            largest_edge = west

        z_units = self.getDistance(largest_edge)
        
        #find x and y based on distance
        x_units = (QRSize)*(pixel_displacement[0]/float(largest_edge))
        y_units = -1 * (QRSize)*(pixel_displacement[1]/float(largest_edge))
        
        return [x_units, y_units, z_units]


    def getDistance(self, length):
        a = 1128.1
        n = -1.1397
        return a*math.pow(length, n)


