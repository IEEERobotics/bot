from collections import namedtuple
import numpy as np
import cv2
import cv2.cv as cv

showKeys = True

ControlRange = namedtuple('ControlRange', ['min', 'zero_min', 'zero_max', 'max'])
forward_range = ControlRange(-100, -20, 20, 100)
strafe_range = ControlRange(-100, -20, 20, 100)

class DesktopControlClient:
    """Desktop-based controller using mouse and/or keyboard input."""
    
    window_name = "Desktop Controller"
    window_width = 640
    window_height = 480
    loop_delay = 20
    
    axes_length = 360
    axes_color = (128, 0, 0)
    limit_color = (64, 0, 0)
    zero_color = (128, 128, 128)
    knob_radius = 15
    knob_color = (0, 0, 128)
    knob_fill_color = (0, 0, 255)
    help_color = (0, 128, 0)
    
    def __init__(self):
        self.forward = 0
        self.strafe = 0
        #self.turn = 0  # TODO add turning
        self.imageOut = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8) # numpy convention: (height, width, depth)
        self.imageCenter = (self.window_width / 2, self.window_height / 2)  # OpenCV convention: (x, y)
        
        # TODO Add mouse callback
    
    def run(self):
        cv2.namedWindow(self.window_name)
        while True:
            self.draw()
            key = cv2.waitKey(self.loop_delay)
            if key != -1:
                keyCode = key & 0x00007f  # key code is in the last 8 bits, pick 7 bits for correct ASCII interpretation (8th bit indicates 
                keyChar = chr(keyCode) if not (key & 0x00ff00) else None # if keyCode is normal (SPECIAL bits are zero), convert to char (str)
                
                if showKeys: print "run(): key = {key:#06x}, keyCode = {keyCode}, keyChar = {keyChar}".format(key=key, keyCode=keyCode, keyChar=keyChar)  # [debug]
                
                if keyCode == 0x1b or keyChar == 'q' or keyChar == 'Q':  # quit
                    break
                elif keyChar == ' ':  # stop/zero out
                    self.forward = 0
                    self.strafe = 0
                elif keyChar == 'w' or keyChar == 'W':  # forward
                    self.forward -= 1
                    if self.forward < forward_range.min:
                        self.forward = forward_range.min
                elif keyChar == 's' or keyChar == 'S':  # backward
                    self.forward += 1
                    if self.forward > forward_range.max:
                        self.forward = forward_range.max
                elif keyChar == 'a' or keyChar == 'A':  # left
                    self.strafe -= 1
                    if self.strafe < strafe_range.min:
                        self.strafe = strafe_range.min
                elif keyChar == 'd' or keyChar == 'D':  # right
                    self.strafe += 1
                    if self.strafe > strafe_range.max:
                        self.strafe = strafe_range.max
                
                # TODO Send commands to server
    
    def draw(self):
        # Clear entire image
        self.imageOut.fill(255)
        
        # Draw axis lines
        cv2.line(self.imageOut, (self.imageCenter[0] - self.axes_length / 2, self.imageCenter[1]), (self.imageCenter[0] + self.axes_length / 2, self.imageCenter[1]), self.axes_color, 2)
        cv2.line(self.imageOut, (self.imageCenter[0], self.imageCenter[1] - self.axes_length / 2), (self.imageCenter[0], self.imageCenter[1] + self.axes_length / 2), self.axes_color, 2)
        
        # Draw limiting rectangle
        cv2.rectangle(self.imageOut, (self.imageCenter[0] + strafe_range.min, self.imageCenter[1] + forward_range.min), (self.imageCenter[0] + strafe_range.max, self.imageCenter[1] + forward_range.max), self.limit_color, 2)
        
        # Draw zero rectangle
        cv2.rectangle(self.imageOut, (self.imageCenter[0] + strafe_range.zero_min, self.imageCenter[1] + forward_range.zero_min), (self.imageCenter[0] + strafe_range.zero_max, self.imageCenter[1] + forward_range.zero_max), self.zero_color, 2)
        
        # Draw control knob
        cv2.circle(self.imageOut, (self.imageCenter[0] + self.strafe, self.imageCenter[1] + self.forward), self.knob_radius, self.knob_fill_color, cv.CV_FILLED)
        cv2.circle(self.imageOut, (self.imageCenter[0] + self.strafe, self.imageCenter[1] + self.forward), self.knob_radius, self.knob_color, 3)
        
        # Add help text
        cv2.putText(self.imageOut, "Move: W/S/A/D, Stop: SPACE, Quit: ESC", (12, self.window_height - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.help_color, 2)
        
        # Show image
        cv2.imshow(self.window_name, self.imageOut)

if __name__ == "__main__":
    DesktopControlClient().run()
