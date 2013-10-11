"""Bot controller client that uses the Leap Motion device."""
# Based on Sample.py included with LeapSDK 0.8.0

import sys
import time
import socket
from collections import namedtuple

try:
    import Leap
    # NOTE Gestures are currently disabled; we could use a tap gesture to fire?
except:
    print "Error: This module cannot be run without the Leap SDK"
    raise

import lib.lib as lib
import server

ControlRange = namedtuple('ControlRange',
                          ['min', 'zero_min', 'zero_max', 'max'])
pitchRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is forward
rollRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is to the right
yawRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is to the left


class LeapControlClient(Leap.Listener):
    """Translates Leap Motion input to commands, sends to a control server."""

    def on_init(self, controller):
        self.logger = lib.get_logger()
        self.sock = None
        self.isMoving = False
        self.isProcessing = False  # Semaphore to prevent asynchronous clashes

        self.serverHost = sys.argv[1] if len(sys.argv) > 1 \
                                      else server.CONTROL_SERVER_HOST
        self.serverPort = int(sys.argv[2]) if len(sys.argv) > 2 \
                                           else server.CONTROL_SERVER_PORT
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.serverHost, self.serverPort))
            self.rfile = self.sock.makefile(mode="rb")
            self.wfile = self.sock.makefile(mode="wb", bufsize=0)
            self.logger.info("Connected to control server at {}:{}".format(
                                                            self.serverHost,
                                                            self.serverPort))
        except socket.error:
            err_msg = "Could not connect to control server at {}:{}".format(
                                                            self.serverHost,
                                                            self.serverPort)
            self.logger.error(err_msg)
            self.sock = None

    def on_connect(self, controller):
        self.logger.info("Connected to Leap device")

    # TODO: Maintain state using on_connect(), on_disconnect()?
    def on_disconnect(self, controller):
        # NOTE: not dispatched when running in a debugger.
        self.logger.info("Disconnected from Leap device")

    def on_exit(self, controller):
        if self.sock is not None:
            #self.wfile.write("\x04\n")  #self.sock.sendall("\x04\n")  # EOF
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock = None
            self.logger.info("Disconnected from control server")

    def on_frame(self, controller):
        if self.isProcessing:
            return
        self.isProcessing = True  # Lock

        frame = controller.frame()  # Get the most recent frame

        forward = 0.
        strafe = 0.
        turn = 0.

        if not frame.hands.is_empty:
            hand = frame.hands[0]  # Get the first hand
            fingers = hand.fingers  # Get list of fingers on this hand
            # NOTE: Useful hand properties: hand.sphere_radius,
            #   hand.palm_position, hand.palm_normal, hand.direction

            # Proceed only if 3 or more fingers are seen and other
            #   criteria met (to prevent flaky behavior)
            position = hand.palm_position
            x = position[0]
            y = position[1]
            z = position[2]
            # TODO Use a state machine to prevent abrupt changes
            # Max hand height (z-position), min fingers; TODO other filters
            if z <= 40 and len(fingers) >= 3:
                # Calculate the hand's pitch, roll, and yaw angles
                pitch = hand.direction.pitch * Leap.RAD_TO_DEG
                roll = hand.palm_normal.roll * Leap.RAD_TO_DEG
                yaw = hand.direction.yaw * Leap.RAD_TO_DEG
                # [debug]
                #print "Pos: {}, pitch: {:+6.2f} deg, roll: {:+6.2f} deg," + \
                #                                " yaw: {:+6.2f} deg".format(
                #                                position, pitch, roll, yaw)
                # [debug]
                #print "Pos: ({:+7.2f}, {:+7.2f}, {:+7.2f}), " + \
                #         "pitch: {:+6.2f} deg, roll: {:+6.2f} deg, " + \
                #         "yaw: {:+6.2f} deg".format(x, y, z, pitch, roll, yaw)

                # Compute control values based on position and orientation
                # * Scheme 1: pitch = forward/backward vel.,
                #   roll = left/right strafe vel., yaw = left/right turn vel.
                # ** Convert pitch => forward velocity
                # If pitch is outside deadband (zero span)
                if pitch <= pitchRange.zero_min \
                        or pitchRange.zero_max <= pitch:
                    # Clamp pitch to [min, max] range
                    if pitch < pitchRange.min:
                        pitch = pitchRange.min
                    elif pitch > pitchRange.max:
                        pitch = pitchRange.max

                    # Compute forward velocity as ratio of current
                    #   pitch to pitch range
                    if pitch < 0:
                        # forward: +ve
                        forward = (pitch - pitchRange.zero_min) / \
                                  (pitchRange.min - pitchRange.zero_min)
                    else:
                        # backward: -ve
                        forward = -(pitch - pitchRange.zero_max) / \
                                   (pitchRange.max - pitchRange.zero_max)

                # ** Convert roll => strafe velocity
                # If roll is outside deadband (zero span)
                if roll <= rollRange.zero_min or rollRange.zero_max <= roll:
                    # Clamp roll to [min, max] range
                    if roll < rollRange.min:
                        roll = rollRange.min
                    elif roll > rollRange.max:
                        roll = rollRange.max

                    # Compute strafe velocity as ratio of current
                    #   roll to roll range
                    if roll < 0:
                        # Strafe left: -ve
                        strafe = (roll - rollRange.zero_min) / \
                                 (rollRange.min - rollRange.zero_min)
                    else:
                        # Strafe right: +ve
                        strafe = -(roll - rollRange.zero_max) / \
                                  (rollRange.max - rollRange.zero_max)

                # ** Convert yaw => turn velocity
                # If yaw is outside deadband (zero span)
                if yaw <= yawRange.zero_min or yawRange.zero_max <= yaw:
                    # Clamp yaw to [min, max] range
                    if yaw < yawRange.min:
                        yaw = yawRange.min
                    elif yaw > yawRange.max:
                        yaw = yawRange.max

                    # Compute turn velocity as ratio of current yaw to
                    #   yaw range (TODO check sign convention)
                    if yaw < 0:
                        # Turn left: +ve
                        turn = (yaw - yawRange.zero_min) / \
                               (yawRange.min - yawRange.zero_min)
                    else:
                        # Turn right: -ve
                        turn = -(yaw - yawRange.zero_max) / \
                                (yawRange.max - yawRange.zero_max)

        # Send control values as command to server (TODO perhaps at a
        #   reduced frequency? use GCode-like conventions? JSON?)
        # TODO move this to a different thread
        cmdStr = None
        if forward == 0. and strafe == 0. and turn == 0.:
            if self.isMoving:
                cmdStr = "stop\n"
                self.isMoving = False
        else:
            cmdStr = "move {:7.2f} {:7.2f} {:7.2f}\n".format(forward * 100,
                                                             strafe * 100,
                                                             turn * 100)
            self.isMoving = True

        if cmdStr is not None:
            print cmdStr,  # [info]
            if self.sock is not None:
                #print "Sending: {}".format(repr(cmdStr))  # [debug]
                self.wfile.write(cmdStr)  # self.sock.sendall(cmdStr)
                #print "Waiting for response..."  # [debug]
                # Server can use response delay to throttle commands
                # TODO check for OK
                response = self.rfile.readline().strip()
                print response  # [info]

        self.isProcessing = False  # release


def main():
    # Create a custom listener and Leap Motion controller
    leapControlClient = LeapControlClient()
    leapController = Leap.Controller()

    # Have the listener receive events from the controller
    # Yep, these names are too confusing!
    leapController.add_listener(leapControlClient)
    time.sleep(0.5)  # Yield so that on_connect() can happen first

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."  # [info]
    sys.stdin.readline()

    # Remove the sample listener when done
    leapController.remove_listener(leapControlClient)


if __name__ == "__main__":
    main()
