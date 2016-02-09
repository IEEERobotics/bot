
import numpy as np
import time

import zbar
import cv2
from PIL import Image
import cv2


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
        self.cam.set(3, 1280)
        self.cam.set(4,720)

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
    def readQR(self):

        QRList = []
        self.cam.grab()
        self.cam.grab()
        self.cam.grab()
        self.cam.grab()
        ret, frame = self.cam.read()        
        # Direct conversion cv -> zbar images did not work.
        # Buffer file used to have native data structures.
        cv2.imwrite('buffer.png', frame)

        # PIL -> zbar
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

            rvec, tvec = cv2.solvePnP(self.qr_verts, points
                                      , self.cam_matrix
                                      , self.dist_coeffs)

            #cv2.line(frame, tl, bl, (100,0,255), 8, 8)
            #cv2.line(frame, bl, br, (100,0,255), 8, 8)
            #cv2.line(frame, br, tr, (100,0,255), 8, 8)
            #cv2.line(frame, tr, tl, (100,0,255), 8, 8)

            QRList.append(QRCode2(tvec, rvec, symbol.data, tr)) 
            count += 1
        if count == 0:
            #print "NO QR FOUND"
            #cv2.imshow('test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return
            continue
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
        print "value: ", targetQR.value
        print "X:     ", targetQR.tvec[0]
        print "Y:     ", targetQR.tvec[1]
        print "====================================="
        #cv2.circle(frame,targetQR.tr, 10, (0,255,0), -1)
        #cv2.imshow('test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

