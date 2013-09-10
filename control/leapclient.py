"""Leap Motion based bot controller."""
# Based on Sample.py included with LeapSDK 0.8.0

import sys
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

ControlRange = namedtuple('ControlRange', ['min', 'zero_min', 'zero_max', 'max'])
pitchRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is forward
rollRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is to the right
yawRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is to the left

class LeapControlClient(Leap.Listener):
  def on_init(self, controller):
    self.logger = lib.get_logger()
    # TODO remove print statements by making logger output INFO messages to console
    self.sock = None
    self.isMoving = False
    self.isProcessing = False  # semaphore to prevent asynchronous clashes
    self.logger.info("Initialized")
    print "LeapControlClient.on_init(): Initialized"
    
    self.serverHost = sys.argv[1] if len(sys.argv) > 1 else server.CONTROL_SERVER_HOST
    self.serverPort = int(sys.argv[2]) if len(sys.argv) > 2 else server.CONTROL_SERVER_PORT
    try:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect((self.serverHost, self.serverPort))
      self.rfile = self.sock.makefile(mode="rb")
      self.wfile = self.sock.makefile(mode="wb", bufsize=0)
      self.logger.info("Connected to control server at {}:{}".format(self.serverHost, self.serverPort))
      print "LeapControlClient.on_init(): Connected to control server at {}:{}".format(self.serverHost, self.serverPort)
    except socket.error:
      self.logger.error("Could not connect to control server at {}:{}".format(self.serverHost, self.serverPort))
      print "LeapControlClient.on_init(): [ERROR] Could not connect to control server at {}:{}".format(self.serverHost, self.serverPort)
      self.sock = None
  
  def on_connect(self, controller):
    self.logger.info("Connected to Leap device")
    print "LeapControlClient.on_connect(): Connected to Leap device"
  
  # TODO maintain state using on_connect(), on_disconnect()?
  def on_disconnect(self, controller):
    # Note: not dispatched when running in a debugger.
    self.logger.info("Disconnected")
    print "LeapControlClient.on_disconnect(): Disconnected"
  
  def on_exit(self, controller):
    self.logger.info("Exiting")
    print "LeapControlClient.on_exit(): Exiting"
    
    if self.sock is not None:
      #self.sock.sendall("\x04\n")  # EOF
      #self.wfile.write("\x04\n")  # EOF
      self.sock.shutdown(socket.SHUT_RDWR)
      self.sock = None
      self.logger.info("Disconnected from control server")
      print "LeapControlClient.on_exit(): Disconnected from control server"
  
  def on_frame(self, controller):
    if self.isProcessing: return
    self.isProcessing = True  # lock
    
    frame = controller.frame()  # get the most recent frame
    
    forward = 0.
    strafe = 0.
    turn = 0.
    
    if not frame.hands.is_empty:
      hand = frame.hands[0]  # get the first hand
      fingers = hand.fingers  # get list of fingers on this hand
      # NOTE Useful hand properties: hand.sphere_radius, hand.palm_position, hand.palm_normal, hand.direction
      
      # Calculate the hand's pitch, roll, and yaw angles; proceed only if 3 or more fingers are seen (to prevent flaky behavior with closed fists)
      # TODO Other filters: min hand.sphere_radius etc.
      if len(fingers) >= 3:
        position = hand.palm_position
        x = position[0]
        y = position[1]
        z = position[2]
        pitch = hand.direction.pitch * Leap.RAD_TO_DEG
        roll = hand.palm_normal.roll * Leap.RAD_TO_DEG
        yaw = hand.direction.yaw * Leap.RAD_TO_DEG
        #print "Pos: {}, pitch: {:+6.2f} deg, roll: {:+6.2f} deg, yaw: {:+6.2f} deg".format(position, pitch, roll, yaw)
        #print "Pos: ({:+7.2f}, {:+7.2f}, {:+7.2f}), pitch: {:+6.2f} deg, roll: {:+6.2f} deg, yaw: {:+6.2f} deg".format(x, y, z, pitch, roll, yaw)
        
        # TODO Compute control values based on position and orientation
        # * Scheme 1: pitch = forward/backward vel., roll = left/right strafe vel., yaw = left/right turn vel.
        # ** Convert pitch => forward velocity
        if pitch <= pitchRange.zero_min or pitchRange.zero_max <= pitch:  # if pitch is outside deadband (zero span)
          # Clamp pitch to [min, max] range
          if pitch < pitchRange.min: pitch = pitchRange.min
          elif pitch > pitchRange.max: pitch = pitchRange.max
          
          # Compute forward velocity as ratio of current pitch to pitch range
          if pitch < 0: forward = (pitch - pitchRange.zero_min) / (pitchRange.min - pitchRange.zero_min)  # forward: +ve
          else: forward = -(pitch - pitchRange.zero_max) / (pitchRange.max - pitchRange.zero_max)  # backward: -ve
        
        # ** Convert roll => strafe velocity
        if roll <= rollRange.zero_min or rollRange.zero_max <= roll:  # if roll is outside deadband (zero span)
          # Clamp roll to [min, max] range
          if roll < rollRange.min: roll = rollRange.min
          elif roll > rollRange.max: roll = rollRange.max
          
          # Compute strafe velocity as ratio of current roll to roll range
          if roll < 0: strafe = (roll - rollRange.zero_min) / (rollRange.min - rollRange.zero_min)  # strafe left: -ve
          else: strafe = -(roll - rollRange.zero_max) / (rollRange.max - rollRange.zero_max)  # strafe right: +ve
        
        # ** Convert yaw => turn velocity
        if yaw <= yawRange.zero_min or yawRange.zero_max <= yaw:  # if yaw is outside deadband (zero span)
          # Clamp yaw to [min, max] range
          if yaw < yawRange.min: yaw = yawRange.min
          elif yaw > yawRange.max: yaw = yawRange.max
          
          # Compute turn velocity as ratio of current yaw to yaw range
          if yaw < 0: turn = (yaw - yawRange.zero_min) / (yawRange.min - yawRange.zero_min)  # turn left: +ve
          else: turn = -(yaw - yawRange.zero_max) / (yawRange.max - yawRange.zero_max)  # turn right: -ve
    
    # Send control values as command to server (TODO perhaps at a reduced frequency? use GCode-like conventions? JSON?)
    # TODO move this to a different thread
    cmdStr = None
    if forward == 0. and strafe == 0. and turn == 0.:
      if self.isMoving:
        cmdStr = "stop\n"
        self.isMoving = False
    else:
      #print "Controls: forward: {:5.2f}, strafe: {:5.2f}, turn: {:5.2f}".format(forward, strafe, turn)
      cmdStr = "move {:5.2f} {:5.2f} {:5.2f}\n".format(forward, strafe, turn)
      self.isMoving = True
    
    if cmdStr is not None and self.sock is not None:
      #print "Sending: {}".format(repr(cmdStr))  # [debug]
      print cmdStr,
      self.wfile.write(cmdStr)  #self.sock.sendall(cmdStr)
      #print "Waiting for response..."  # [debug]
      response = self.rfile.readline().strip()  # server can use response delay to throttle commands (TODO check for OK)
      print response
    
    self.isProcessing = False  # release



def main():
  # Create a custom listener and Leap Motion controller
  leapControlClient = LeapControlClient()
  leapController = Leap.Controller()
  
  # Have the listener receive events from the controller
  leapController.add_listener(leapControlClient)
  
  # Keep this process running until Enter is pressed
  print "Press Enter to quit..."
  sys.stdin.readline()
  
  # Remove the sample listener when done
  leapController.remove_listener(leapControlClient)


if __name__ == "__main__":
  main()
