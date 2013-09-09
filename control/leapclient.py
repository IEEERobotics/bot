"""Leap Motion based bot controller."""
# Based on Sample.py included with LeapSDK 0.8.0

import sys
import socket

try:
  import Leap
  # NOTE Gestures are currently disabled; we could use a tap gesture to fire?
except:
  print "Error: This module cannot be run without the Leap SDK"
  raise

import lib.lib as lib
import server

class LeapControlClient(Leap.Listener):
  def on_init(self, controller):
    self.logger = lib.get_logger()
    # TODO remove print statements by making logger output INFO messages to console
    self.sock = None
    self.logger.info("Initialized")
    print "LeapControlClient.on_init(): Initialized"
    
    self.serverHost = sys.argv[1] if len(sys.argv) > 1 else server.CONTROL_SERVER_HOST
    self.serverPort = sys.argv[2] if len(sys.argv) > 2 else server.CONTROL_SERVER_PORT
    try:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect((self.serverHost, self.serverPort))
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
      #self.sock.sendall('\x04')  # EOF
      self.sock.shutdown(socket.SHUT_RDWR)
      self.sock = None
      self.logger.info("Disconnected from control server")
      print "LeapControlClient.on_exit(): Disconnected from control server"
  
  def on_frame(self, controller):
    frame = controller.frame()  # get the most recent frame
    
    if not frame.hands.empty:
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
        print "Pos: ({:+7.2f}, {:+7.2f}, {:+7.2f}), pitch: {:+6.2f} deg, roll: {:+6.2f} deg, yaw: {:+6.2f} deg".format(x, y, z, pitch, roll, yaw)
        
        # TODO Compute control values based on position and orientation
        forward = 0
        backward = 0
        left = 0
        right = 0
        
        # TODO Send control values as command to server (perhaps at a reduced frequency? use GCode-like conventions? JSON?)


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
