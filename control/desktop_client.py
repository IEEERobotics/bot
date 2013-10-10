import sys
import socket
import threading
from collections import namedtuple

import numpy as np
import cv2
import cv2.cv as cv

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

import lib.lib as lib
import server

showKeys = False  # True  # [debug]

ControlRange = namedtuple('ControlRange',
                          ['min', 'zero_min', 'zero_max', 'max'])
forward_range = ControlRange(-100, -25, 25, 100)
strafe_range = ControlRange(-100, -25, 25, 100)
turn_range = ControlRange(-100, -25, 25, 100)


# TODO(dfarrell07): Inherit from object
class DesktopControlClient:
    """Desktop-based controller using mouse and/or keyboard input."""

    window_name = "Desktop Controller"
    window_width = 640
    window_height = 480
    loop_delay = 20

    axes_length = 360
    axes_color = (64, 0, 0)
    limit_color = (128, 0, 0)
    zero_color = (128, 128, 128)
    knob_radius = 15
    knob_color = (0, 0, 128)
    knob_fill_color = (0, 0, 255)
    help_color = (0, 128, 0)
    help_text = "Move: WSAD/drag; Stop: SPACE; Quit: ESC"

    def __init__(self):
        self.logger = lib.get_logger()
        self.config = lib.load_config()
        self.sock = None
        self.keepRunning = True
        # Exclusive semaphore to prevent asynchronous clashes
        self.isProcessing = threading.BoundedSemaphore()
        # NOTE: This semaphore mechanism doesn't really work because only
        #   one thread ("MainThread") is actually executed
        # TODO: Spawn two separate threads, one for getting
        #   user input to set control values and one for sending
        #   commands based on those control values
        self.isMoving = False

        # Build socket and connect to server
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REQ)
        self.sock.connect(self.config["server_port"])
        self.logger.info("Connected to control server at {}".format(
                                                            self.sock))

        self.forward = 0
        self.strafe = 0
        self.turn = 0  # TODO: Add turning

        # Numpy convention: (height, width, depth)
        self.imageOut = np.zeros((self.window_height, self.window_width, 3),
                                  dtype=np.uint8)
        # OpenCV convention: (x, y)
        self.imageCenter = (self.window_width / 2, self.window_height / 2)

    def cleanUp(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            self.context.term()
            self.logger.info("Disconnected from control server")

    def run(self):
        cv2.namedWindow(self.window_name)
        cv.SetMouseCallback(self.window_name, self.onMouse, param=None)

        try:
            while self.keepRunning:
                self.draw()
                key = cv2.waitKey(self.loop_delay)
                if key != -1:
                    self.onKeyPress(key)
        except KeyboardInterrupt:
            self.logger.warn("Why kill me with a Ctrl+C? Try Esc next time.")
            self.isProcessing.release()

        self.cleanUp()

    def onKeyPress(self, key):
        # Key code is in the last 8 bits, pick 7 bits for correct
        #   ASCII interpretation (8th bit indicates ?)
        keyCode = key & 0x00007f
        # If keyCode is normal (SPECIAL bits are zero), convert to char (str)
        keyChar = chr(keyCode) if not (key & 0x00ff00) else None

        #TODO(dfarrell): Remove before commit
        showKeys = True
        if showKeys:
            self.logger.debug("key = {}, keyCode = {}, keyChar = {}".format(
                                                       key, keyCode, keyChar))

        if keyCode == 0x1b or keyChar == 'q' or keyChar == 'Q':  # quit
            self.keepRunning = False
            self.forward = 0
            self.strafe = 0
            self.turn = 0
        elif keyChar == ' ':  # stop/zero out
            self.forward = 0
            self.strafe = 0
            self.turn = 0
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
        else:
            self.logger.warning("Unknown key = {}, keyCode = {}, " + \
                                                   "keyChar = {}".format(
                                                   key,
                                                   keyCode,
                                                   keyChar))
            return

        self.sendCommand()

    def onMouse(self, event, x, y, flags, param=None):
        # [debug]
        #print "DesktopControlClient.onMouse(): {} @ ({}, {}) " + \
        #                            "[flags = {}]".format(event, x, y, flags)
        if event == cv.CV_EVENT_LBUTTONUP:  # stop when left button is released
            #print "stop"  # [debug]
            self.forward = 0
            self.strafe = 0
        # Move when left button is held down
        elif event == cv.CV_EVENT_MOUSEMOVE and \
                flags & cv.CV_EVENT_FLAG_LBUTTON:
            #print "move ({}, {})".format(x, y)  # [debug]
            self.forward = y - self.imageCenter[1]
            if self.forward < forward_range.min:
                self.forward = forward_range.min
            elif self.forward > forward_range.max:
                self.forward = forward_range.max

            self.strafe = x - self.imageCenter[0]
            if self.strafe < strafe_range.min:
                self.strafe = strafe_range.min
            elif self.strafe > strafe_range.max:
                self.strafe = strafe_range.max
        else:
            return

        self.sendCommand()

    def sendCommand(self):
        # TODO: Check if this is actually not blocking
        if not self.isProcessing.acquire(blocking=False):
            return
        self.logger.debug("[{}] Acquired".format(
                                          threading.current_thread().name))

        # Take snapshot of current control values
        # NOTE: Y-flip
        # TODO(dfarrell07): Convert forward, strafe and turn to properties
        forward = 0 if forward_range.zero_min < self.forward < \
                                                forward_range.zero_max \
                                                else -self.forward
        strafe = 0 if strafe_range.zero_min < self.strafe < \
                                              strafe_range.zero_max \
                                              else self.strafe
        turn = 0 if turn_range.zero_min < self.turn < turn_range.zero_max \
                 else self.turn
        # TODO Decouple input resolution from output resolution by
        #   defining a scaling transformation

        cmdStr = None
        if forward == 0 and strafe == 0 and turn == 0:
            if self.isMoving:
                cmdStr = "{cmd: fwd_strafe_turn, " + \
                         "opts: {fwd: 0, strafe: 0, turn: 0}}"
                self.isMoving = False
        else:
            # '{{' and '}}' give '{' and '}' after .format call
            # NOTE: The reason there is an unballenced number of {} in the
            #   following two lines is because format is being called on the
            #   second line only, so it needs }} to get }, where the first
            #   only needs the typical {.
            cmdStr = "{cmd: fwd_strafe_turn, " + \
                      "opts: {{fwd: {}, strafe: {}, turn: {}}}}}".format(
                                                            forward,
                                                            strafe,
                                                            turn)
            self.isMoving = True

        self.logger.debug("cmdStr: {}".format(cmdStr))
        if cmdStr is not None:
            if self.sock is not None:
                self.logger.debug("Sending: {}".format(repr(cmdStr)))
                # TODO(dfarrell07): Convert to ZMQ call
                self.sock.send(cmdStr)
                # Server can use response delay to throttle commands
                #   TODO check for OK
                # TODO(dfarrell07): Convert to ZMQ call
                self.logger.debug("About to block for recv")
                response = self.sock.recv()
                self.logger.debug("Returned from block to recv")
                #response = self.rfile.readline().strip()
                self.logger.info("Response: {}".format(response))

        # [debug]
        self.logger.debug("[{}] Releasing".format(
                                           threading.current_thread().name))
        self.isProcessing.release()

    def draw(self):
        # Clear entire image
        self.imageOut.fill(255)

        # Draw axis lines
        cv2.line(
            self.imageOut,
            (self.imageCenter[0] - self.axes_length / 2, self.imageCenter[1]),
            (self.imageCenter[0] + self.axes_length / 2, self.imageCenter[1]),
            self.axes_color, 2)
        cv2.line(
            self.imageOut,
            (self.imageCenter[0], self.imageCenter[1] - self.axes_length / 2),
            (self.imageCenter[0], self.imageCenter[1] + self.axes_length / 2),
            self.axes_color, 2)

        # Draw zero (deadband) regions and rectangle
        cv2.rectangle(
            self.imageOut,
            (self.imageCenter[0] + strafe_range.min,
                self.imageCenter[1] + forward_range.zero_min),
            (self.imageCenter[0] + strafe_range.max,
                self.imageCenter[1] + forward_range.zero_max),
            self.zero_color, 1)
        cv2.rectangle(
            self.imageOut,
            (self.imageCenter[0] + strafe_range.zero_min,
                self.imageCenter[1] + forward_range.min),
            (self.imageCenter[0] + strafe_range.zero_max,
                self.imageCenter[1] + forward_range.max),
            self.zero_color, 1)
        cv2.rectangle(
            self.imageOut,
            (self.imageCenter[0] + strafe_range.zero_min,
                self.imageCenter[1] + forward_range.zero_min),
            (self.imageCenter[0] + strafe_range.zero_max,
                self.imageCenter[1] + forward_range.zero_max),
            self.zero_color, 2)

        # Draw limiting rectangle
        cv2.rectangle(
            self.imageOut,
            (self.imageCenter[0] + strafe_range.min,
                self.imageCenter[1] + forward_range.min),
            (self.imageCenter[0] + strafe_range.max,
                self.imageCenter[1] + forward_range.max),
            self.limit_color, 2)

        # Add help text
        cv2.putText(
            self.imageOut,
            self.help_text,
            (12, self.window_height - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            self.help_color, 2)

        # TODO: Cache drawing till this point as static
        #   image and blit every frame

        # Draw control knob and vector
        cv2.line(
            self.imageOut,
            self.imageCenter,
            (self.imageCenter[0] + self.strafe,
                self.imageCenter[1] + self.forward),
            self.knob_color, 2)
        cv2.circle(
            self.imageOut,
            (self.imageCenter[0] + self.strafe,
                self.imageCenter[1] + self.forward),
            self.knob_radius,
            self.knob_fill_color, cv.CV_FILLED)

        cv2.circle(
            self.imageOut,
            (self.imageCenter[0] + self.strafe,
                self.imageCenter[1] + self.forward),
            self.knob_radius,
            self.knob_color, 3)

        # Show image
        cv2.imshow(self.window_name, self.imageOut)


if __name__ == "__main__":
    DesktopControlClient().run()
