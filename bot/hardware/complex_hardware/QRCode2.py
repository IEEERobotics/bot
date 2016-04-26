import os
import zbar
from PIL import Image
import cv2
import numpy as np
import time
import bot.lib.lib as lib
import math


class QRCode2(object):
    def __init__(self, tvec, value, top_right):
        self.tvec = tvec
        self.value = value
        self.tr = top_right
        
class Block(object):
    def __init__(self, size, color):
        self.size = size
        self.color = color
