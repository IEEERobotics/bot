"""Direct control server that responds to commands, potentially from a remote location."""

import os
import threading
import SocketServer
import signal
import logging
import time
import unittest
from math import fabs

import lib.lib as lib
from driver.mec_driver import MecDriver

CONTROL_SERVER_HOST = "0.0.0.0"
CONTROL_SERVER_PORT = 60000

COMMAND_BUFFER_SIZE = 64  # bytes
COMMAND_PROMPT = None  #"> "  # set to None to prevent printing a prompt
RESPONSE_DELAY = 0.05  # secs; used to throttle control messages (>= some multiple of drive motor PWM period, currently 1 ms)

class ControlRequestHandler(SocketServer.StreamRequestHandler):
  """Handles incoming commands and actuates bot accordingly."""
  
  def handle(self):
    logger = lib.get_logger()  # NOTE a logger for each client request (request lasts for entire session, so this shouldn't be too bad)
    
    clientHost, clientPort = self.client_address
    myThread = threading.current_thread()
    logger.info("[ControlRequestHandler/{}] Serving client {}:{}".format(myThread.name, clientHost, clientPort))
    
    controlServer = ControlServer.getInstance()  # get singleton instance of ControlServer
    
    while True:
      if COMMAND_PROMPT is not None: self.wfile.write(COMMAND_PROMPT)  #self.request.sendall(COMMAND_PROMPT)
      data = self.rfile.readline().strip()
      if not data or data.startswith('\x04'): break  # client has quit or EOF received, nothing more to do here
      
      #print "[ControlRequestHandler/{}] Recvd: {}".format(myThread.name, data)  # [debug]
      tokens = data.split()  # split on whitespace, collapse delimiters; TODO use JSON/YAML/ZMQ?
      cmd = tokens[0]
      isValid = False  # whether the command is valid or not
      if cmd == "stop" or cmd == "s":
        # Stop bot by setting speed to zero
        controlServer.driver.move(0, 0)
        isValid = True
      elif cmd == "move" or cmd == "m":
        # Parse movement parameters and move bot in desired direction
        try:
          forward = float(tokens[1])
          strafe = float(tokens[2])
          turn = float(tokens[3])
          if fabs(turn) > fabs(forward) and fabs(turn) > fabs(strafe):  # rotate only when turn dominates
            controlServer.driver.rotate(turn)
          else:
            controlServer.driver.move_forward_strafe(forward, strafe)
          isValid = True
        except Exception as e:
          pass  # will be reported back to client as ERROR
      
      # Send response
      response = "OK\n" if isValid else "ERROR (cmd: {})\n".format(cmd)  # ACK
      time.sleep(RESPONSE_DELAY)  # response delay to throttle messages
      self.wfile.write(response)
    
    # Clean-up when done serving client
    if controlServer.driver.speed > 0: controlServer.driver.move(0, 0)  # stop bot, in case still moving
    logger.info("[ControlRequestHandler/{}] Done.".format(myThread.name))


class ControlServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  """Listens on a designated port for client connections. Singleton pattern."""
  instance = None
  
  @classmethod
  def getInstance(cls):
    if cls.instance is None:
      cls.instance = ControlServer((CONTROL_SERVER_HOST, CONTROL_SERVER_PORT), ControlRequestHandler)
      cls.instance.driver = MecDriver()  # should Driver/MecDriver be made a singleton?
    return cls.instance


class TestControlServer(unittest.TestCase):
  """Spawn an instance of ControlServer with simulated hardware."""
  # TODO move this to /tests/ and combine with a client test
  
  def setUp(self):
    """Setup test hardware files and create mec_driver object"""
    config = lib.load_config()
    
    # Store original test flag, set to true
    self.orig_test_state = config["testing"]
    lib.set_testing(True)
    
    # List of directories simulating beaglebone
    self.test_dirs = []
    
    # Collect simulated hardware test directories
    for motor in config["drive_motors"]:
      self.test_dirs.append(config["test_pwm_base_dir"]
                                   + str(motor["PWM"]))
    
    # Reset simulated directories to default
    for test_dir in self.test_dirs:
      # Create test directory
      if not os.path.exists(test_dir):
        os.makedirs(test_dir)
      
      # Set known value in all simulated hardware
      with open(test_dir + "/run", "w") as f:
        f.write("0\n")
      with open(test_dir + "/duty_ns", "w") as f:
        f.write("0\n")
      with open(test_dir + "/period_ns", "w") as f:
        f.write("1000000\n")
  
  def do_runServer(self):
    run()
  
  def tearDown(self):
    """Restore testing flag state in config file."""
    lib.set_testing(self.orig_test_state)

def run():
  # Get a logger
  logger = lib.get_logger()
  
  # Create control server
  controlServer = ControlServer.getInstance()
  
  # Create a thread to run the server in
  serverThread = threading.Thread(target=controlServer.serve_forever)
  serverThread.daemon = True
  
  '''
  # Define an interrupt handler to stop the server, and register it
  def interruptHandler(signum, frame):
    #print "run().interruptHandler(): signum = {}".format(signum)  # [debug]
    logger.info("Stopping ControlServer instance...")
    controlServer.shutdown()
    # Unregister this handler so that default behavior can take over
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
  
  signal.signal(signal.SIGINT, interruptHandler)
  signal.signal(signal.SIGTERM, interruptHandler)
  '''
  
  # Now start the server thread, and wait for it to finish
  serverThread.start()
  serverHost, serverPort = controlServer.server_address
  logger.info("ControlServer started on thread {}, listening at {}:{}".format(serverThread.name, serverHost, serverPort))
  
  try:
    while serverThread.isAlive():
      time.sleep(1)  # or: serverThread.join(1), or: sys.stdin.readline() to wait for an Enter key (no while loop)
  except KeyboardInterrupt:
    logger.info("Stopping ControlServer instance...")
    controlServer.shutdown()
  
  logger.info("Done.")


if __name__ == "__main__":
  run()  # NOTE this will run with driver connected to physical hardware pins!
