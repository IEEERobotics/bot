import os
import sympy
from sympy import *

import zbar
from PIL import Image
import cv2
import numpy as np
import time

class QRCode:
    def __init__(self,tvec,rvec,value, top_right):
        self.tvec = tvec
        self.rvec = rvec
        self.value = value
        self.tr = top_right
        
class Camera:
    def  __init__(self):
        # Image processing 
        self.cam = cv2.VideoCapture(0)

        # Camera dimensions had to be set manually
        #self.cam.set(3,1280)
        #self.cam.set(4,720)

        # QR scanning tools.
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')

        # Figure out what camera is being used
        #cam_model = arm_config["camera_model"]

        # Constants based on calibration for image processing
        self.cam_matrix  = np.float32(
                        [[8.0792012531407818e+02, 0.0, 3.1950000000000000e+02],
                        [0.0, 8.0792012531407818e+02, 2.3950000000000000e+02],
                        [0.0, 0.0,       1.0]])
        self.dist_coeffs = np.float32([
                        -2.5270839161968561e-01
                        , 7.9500908841531919e+00
                        , 0.0
                        , 0.0
                        , -5.7250126941290183e+01])

        # initialize vertices of QR code
        l = 1.5
        self.qr_verts = np.float32([[-l/2, -l/2, 0],
                            [-l/2,  l/2, 0],
                            [ l/2, -l/2, 0],
                            [ l/2,  l/2, 0]])
        
        
        
    def readQR(self):
        
        while(True):
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

                ret, rvec, tvec = cv2.solvePnP(self.qr_verts, points
                                          , self.cam_matrix
                                          , self.dist_coeffs)

                cv2.line(frame, tl, bl, (100,0,255), 8, 8)
                cv2.line(frame, bl, br, (100,0,255), 8, 8)
                cv2.line(frame, br, tr, (100,0,255), 8, 8)
                cv2.line(frame, tr, tl, (100,0,255), 8, 8)

                QRList.append(QRCode(tvec, rvec, symbol.data, tr)) 
                count += 1
            if count == 0:
                #print "NO QR FOUND"
                cv2.imshow('test', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
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
            cv2.circle(frame,targetQR.tr, 10, (0,255,0), -1)
            cv2.imshow('test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cam.release()
        cv2.destroyAllWindows()