import cv2
import zbar
from math import sqrt

import numpy as np

# Size of qr

class QRCode(object):
    """ Represents a QR code.
    Locations are not accurate.
    Useful properties:
        self.value: the value of the code.
        self.points: numpy 
        self.X: X value of center
        self.Y: Y value of center

        """

    def __init__(self, symbol, size):

        # Raw object from zbar.
        self.symbol = symbol        
        self.value = self.symbol.data

        # Begin Processing symbol
        self.topLeft, self.bottomLeft, self.bottomRight, self.topRight = [item for item in self.symbol.location]

        self.points = np.float32(symbol.location)
        self.set_centroid_location()

        l = size
        self.verts = np.float32([[-l/2, -l/2, 0],
                                 [-l/2,  l/2, 0],
                                 [l/2,  -l/2, 0],
                                 [l/2,   l/2, 0]])
        self.rvec = [999]*3
        self.tvec = [999]*3
        self.displacement = []
        self.displacement_2d = []
        
    def __str__(self):
        return "value: %s \n Location: %s \n Verts: %s" % \
                (self.value, self.centroid_location, self.points)

    @property
    def tvec(self):
        return self.__tvec

    @tvec.setter
    def tvec(self, vec):
        self.__tvec = vec
        self.displacement_2d = sqrt(vec[0]**2 + vec[1]**2)
        self.displacement = sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)

    @property
    def points(self):
        return self.__points

    @points.setter
    def points(self, value):
        """Numpy array of corners of QR code. """
        self.__points = np.float32(value)
 
    def set_centroid_location(self):
        x_sum = 0
        y_sum = 0
        # calculate center from x and y of points
        for item in self.symbol.location:
            x_sum += item[0]
            y_sum += item[1]
        X = x_sum / 4
        Y = y_sum /4
        self.centroid_location =  (X, Y)
