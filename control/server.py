"""Direct control server that responds to commands, potentially from a remote location."""

import threading
import SocketServer
import signal
import logging
import time

import lib.lib as lib

CONTROL_SERVER_HOST = "localhost"
CONTROL_SERVER_PORT = 5005

COMMAND_BUFFER_SIZE = 64  # bytes
COMMAND_PROMPT = None  #"> "  # set to None to prevent printing a prompt

class ControlRequestHandler(SocketServer.StreamRequestHandler):
  """Handles incoming commands and actuates bot accordingly."""
  
  def handle(self):
    logger = lib.get_logger()  # NOTE a logger for each client request (request lasts for entire session, so this shouldn't be too bad)
    # TODO remove print statements by making logger output INFO messages to console
    
    clientHost, clientPort = self.client_address
    myThread = threading.current_thread()
    logger.info("[{}] Serving client {}:{}".format(myThread.name, clientHost, clientPort))
    print "[{}] Serving client {}:{}".format(myThread.name, clientHost, clientPort)
    
    while True:
      if COMMAND_PROMPT is not None: self.wfile.write(COMMAND_PROMPT)  #self.request.sendall(COMMAND_PROMPT)
      #print "Waiting for input..."  # [debug]
      data = self.rfile.readline().strip()
      if not data or data.startswith('\x04'): break  # client has quit or EOF received, nothing more to do here
      
      #print "[{}] Recvd: {}".format(myThread.name, data)  # [debug]
      tokens = data.split(' ')
      cmd = tokens[0]
      isValid = False  # whther the command is valid or not
      if cmd == "stop" or cmd == "s":
        # TODO stop bot
        isValid = True
      elif cmd == "move" or cmd == "m":
        # TODO parse movement parameters and move bot in desired direction
        isValid = True
      
      # TODO use response delay to throttle messages
      response = "OK\n" if isValid else "ERROR (cmd: {})\n".format(cmd)  # ACK
      self.wfile.write(response)
    
    logger.info("[{}] Done.".format(myThread.name))
    print "[{}] Done.".format(myThread.name)


class ControlServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  """Listens on a designated port for client connections."""
  pass

def main():
  # Get a logger
  logger = lib.get_logger()
  # TODO remove print statements by making logger output INFO messages to console
  #logger.setLevel(logging.INFO)
  print "main(): Got logger with level: {}".format(logger.level)
  
  # Create control server
  controlServer = ControlServer((CONTROL_SERVER_HOST, CONTROL_SERVER_PORT), ControlRequestHandler)
  
  # Create a thread to run the server in
  serverThread = threading.Thread(target=controlServer.serve_forever)
  serverThread.daemon = True
  
  '''
  # Define an interrupt handler to stop the server, and register it
  def interruptHandler(signum, frame):
    print "main().interruptHandler(): signum = {}".format(signum)
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
  logger.info("ControlServer instance started on thread {}, listening at {}:{}".format(serverThread.name, serverHost, serverPort))
  print "main(): ControlServer instance started on thread {}, listening at {}:{}".format(serverThread.name, serverHost, serverPort)
  
  try:
    while serverThread.isAlive():
      time.sleep(1)  # or: serverThread.join(1)
  except KeyboardInterrupt:
    logger.info("Stopping ControlServer instance...")
    print "main(): Stopping ControlServer instance..."
    controlServer.shutdown()
  
  logger.info("Done.")
  print "main(): Done."

if __name__ == "__main__":
  main()
