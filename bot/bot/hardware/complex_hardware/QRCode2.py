import os
import zbar
from PIL import Image
import cv2
import numpy as np
import time
import bot.lib.lib as lib
import math


class QRCode2:
    def __init__(self, tvec, value, top_right):
        self.tvec = tvec
        self.value = value
        self.tr = top_right
        
class Camera:
    def  __init__(self):
        # Image processing 
        self.cam = cv2.VideoCapture(-1)

        # Camera dimensions had to be set manually
        self.cam.set(3,1280)
        self.cam.set(4,720)

        # QR scanning tools.
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')

        # Figure out what camera is being used
        self.bot_config = lib.get_config()
        cam_model = self.bot_config["camera_model"]

        # Constants based on calibration for image processing
        self.cam_matrix  = np.float32(
                        self.bot_config[cam_model]["camera_matrix"])
        self.dist_coeffs = np.float32(
                        self.bot_config[cam_model]["distortion_coefficients"])

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
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            frame = cv2.bilateralFilter(frame, 9, 75, 75) 
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

                #cv2.line(frame, tl, bl, (100,0,255), 8, 8)
                #cv2.line(frame, bl, br, (100,0,255), 8, 8)
                #cv2.line(frame, br, tr, (100,0,255), 8, 8)
                #cv2.line(frame, tr, tl, (100,0,255), 8, 8)

                QRList.append(QRCode(tvec, rvec, symbol.data, tr)) 
                count += 1
            if count == 0:
                #print "NO QR FOUND"
                #cv2.imshow('test', frame)
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
        
        
    def QRSweep(self):
        
        QRList = []
        self.cam.grab()
        self.cam.grab()
        self.cam.grab()
        self.cam.grab()
        ret, frame = self.cam.read()   
        # Direct conversion cv -> zbar images did not work.
        # Buffer file used to have native data structures.

        # PIL -> zbar

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, frame = cv2.threshold(gray,95,255,cv2.THRESH_BINARY)
        cv2.imwrite('buffer.png', frame)
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

            #cv2.line(frame, tl, bl, (100,0,255), 8, 8)
            #cv2.line(frame, bl, br, (100,0,255), 8, 8)
            #cv2.line(frame, br, tr, (100,0,255), 8, 8)
            #cv2.line(frame, tr, tl, (100,0,255), 8, 8)

            QRList.append(QRCode2(tvec, symbol.data, tr)) 
            count += 1

        if count == 0:
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

        resX = 1280
        resY = 720
        center = [resX/2, resY/2]

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
        a = 2453.3
        n = -1.0235
        return a*math.pow(length, n)



    