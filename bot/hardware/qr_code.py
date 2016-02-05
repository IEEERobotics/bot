import cv2
import zbar

import numpy as np

class QRCode(object):
    """ Represents a QR code.
    Locations are not accurate.
    Useful properties:
        self.value: the value of the code.
        self.verts: numpy 
        self.X: X value of center
        self.Y: Y value of center

        """

    def __init__(self, symbol):
        # Raw object from zbar.
        self.symbol = symbol
        
        self.value = self.symbol.data

        # Begin Processing symbol
        self.topLeft, self.bottomLeft, self.bottomRight, self.topRight = [item for item in self.symbol.location]

        self.verts = np.float32(symbol.location)
         
        # calculate center from x and y of verts
        for item in self.symbol.location:
            x_sum += item(0)
            y_sum += item(1)
        self.X = x_sum / 4
        self.Y = y_sum /4
       
         
