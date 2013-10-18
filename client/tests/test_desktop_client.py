"""Test cases for desktop client."""
import sys
import os
import unittest
from multiprocessing import Process
from subprocess import Popen

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import zmq
except ImportError:
    print "Failed to import zmq"
    sys.exit(1)

try:
    import lib.lib as lib
    import server as server_mod
    import client.desktop_client as dclient_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestBasic(test_bot.TestBot):

    """Basic test, just get things running."""

    def setUp(self):
        """Build desktop_client"""
        # Run general bot test setup
        super(TestBasic, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.config["server_port"])

        # Build desktop client and tell it to run
        self.dclient = dclient_mod.DesktopControlClient()
        #self.dclient.run()

    def tearDown(self):
        """Stop client, kill server, restore testing flag in config file."""
        self.dclient.cleanUp()
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestBasic, self).tearDown()

    def testBasic(self):
        """Test sending a basic command."""
        # Set internal state of clinet
        self.dclient.forward = 50
        self.dclient.strafe = 0
        self.dclient.rotate = 0

        # Cause client to send command to server
        self.dclient.sendCommand()
