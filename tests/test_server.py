"""Test cases for lightweight server."""
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
    import server
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()

class TestServer(unittest.TestCase):

    """Basic tests for command server."""

    def setUp(self):
        """Build server and set it to listen."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server
        self.server = Popen(["./server.py"])

        # Build socket and connect to server
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://*:60000")

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testInvalidMsgType(self):
        """Test sending a non-dict message."""
        self.socket.send("not_a_dict")
        reply = self.socket.recv()
        assert reply == "Error: Unable to convert message to dict"

    def testInvalidCmdKey(self):
        """Test sending a message without a valid cmd key."""
        self.socket.send("{cmd_blah : move, opts : {}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'cmd' key given"

    def testInvalidOptsKey(self):
        """Test sending a message without a valid opts key."""
        self.socket.send("{cmd : move, opts_blah : {}}")
        reply = self.socket.recv()
        print reply
        assert reply == "Error: No 'opts' key given"

    def testInvalidCmdValue(self):
        """Test sending a message with an invalid cmd value."""
        self.socket.send("{cmd : wrong_cmd, opts : {}}")
        reply = self.socket.recv()
        assert reply == "Error: Unknown cmd wrong_cmd"
