
import numpy as np
import time

import zbar
import cv2
from PIL import Image
import cv2


import bot.lib.lib as lib
from bot.hardware.qr_code import QRCode

class Camera(object):

    l = 1.5
    qr_verts = np.float32([[-l/2, -l/2, 0],
                            [-l/2,  l/2, 0],
                            [ l/2, -l/2, 0],
                            [ l/2,  l/2, 0]])

    def __init__(self, cam_config):
        # Recieves 

        self.logger = lib.get_logger()
        
        self.cam.set(3, 1280)
        self.cam.set(4,720)

        # QR scanning tools
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')
        
        # Camera calibrations
        self.cam_matrix = np.float32(cam_config["camera_matrix"])
        self.dist_coeffs = np.float32(cam_config["distance_coefficients"])

    def apply_filters(self, frame):
        """Attempts to improve viewing by applying filters """
        # grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        frame = cv2.bilateralFilter(frame, 9, 75, 75) 
        return frame

    @lib.api_call
    def get_current_frame(self):
        self.cam.grab()        
        self.cam.grab()        
        self.cam.grab()        
        self.cam.grab()       
        return self.cam.read()
 
    def get_zbar_im(self, frame):
        cv2.imwrite('buffer.png', frame)
        pil_im = Image.open('buffer.png').convert('L')
        width, height = pil_im.size
        raw = pil_im.tobytes()

        return zbar.Image(width, height, 'Y800', raw)

    @lib.api_call
    def get_qr_list(self, frame):
        """Recieves frame, assuming it's already been sanitizes, 
        and returns a list of all qr codes in it.
        """
 
        z_im = get_zbar_im(frame)
        self.scanner.scan(z_im)
        qr_list = []
        # Gather list of all QR objects
        for symbol in z_im:
            tl, bl, br, tr = [item for item in symbol.location]
            points = np.float32(np.float32(symbol.location))
            qr_list.append(QRCode(symbol, self.l))
  
    @lib.api_call
    def sort_closest_qr(self, qr_list):
        """returns sortest list with closest qr first"""

        for code in qr_list:
            code.rvec, code.tvec = cv2.solvePnP(self.verts
                                               , code.points
                                               , self.cam_matrix
                                               , self.dist_coeffs)
            
        # Finds qr with smallest displacement 
        qr_list.sort(key=lambda qr: qr.displacement, reverse=False)
        return qr_list

    @lib.api_call 
    def infinite_demo(self):
        while True:

            ret, frame = self.get_current_frame()
    
            clean_frame = self.apply_filters(frame)

            z_im = get_zbar_im(clean_frame)

            # find all symbols in obj
            scanner.scan(z_im)
            
            found_qrs = get_qr_list(z_im)

            sorted_qr = sort_closest_qr(found_qrs)

            targetQR = sorted_qr[0]

            del(z_im)
            del(pil_im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cam.release()
        cv2.destroyAllWindows

                
