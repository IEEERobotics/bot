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


class TestHandleMessage(unittest.TestCase):

    """Basic tests handle message method."""

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testInvalidMsgType(self):
        """Test sending a non-dict message."""
        self.socket.send("not_a_dict")
        reply = self.socket.recv()
        assert reply == "Error: Unable to convert message to dict"

    def testInvalidCmdKey(self):
        """Test sending a message without a valid cmd key."""
        self.socket.send("{cmd_blah: move, opts: {}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'cmd' key given"

    def testInvalidOptsKey(self):
        """Test sending a message without a valid opts key."""
        self.socket.send("{cmd: move, opts_blah: {}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'opts' key given"

    def testInvalidCmdValue(self):
        """Test sending a message with an invalid cmd value."""
        self.socket.send("{cmd: wrong_cmd, opts: {}}")
        reply = self.socket.recv()
        assert reply == "Error: Unknown cmd wrong_cmd"

    def testInvalidYAML(self):
        """Test sending a message that's invalid YAML.

        Note that the problem with the sent message is that it's
        missing a closing bracket.

        """
        self.socket.send("{cmd: move, opts: {speed: 50, angle: 0}")
        reply = self.socket.recv()
        assert reply == "Error: Unable to parse message as YAML"


class TestHandleFwdStrafeTurn(unittest.TestCase):

    """Test fwd, strafe and turn commands.

    TODO: More test cases.

    """

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testValid(self):
        """Test fwd_strafe_turn message that's perfectly valid."""
        self.socket.send("{cmd: fwd_strafe_turn, " + \
                         "opts: {fwd: 50, turn: 0, strafe: 0}}")
        reply = self.socket.recv()
        assert reply == "Success: {'fwd': 50, 'turn': 0, 'strafe': 0}", reply


class TestHandleMove(unittest.TestCase):

    """Test move commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testValid(self):
        """Test move message that's perfectly valid."""
        self.socket.send("{cmd: move, opts: {speed: 50, angle: 0}}")
        reply = self.socket.recv()
        assert reply == "Success: {'speed': 50, 'angle': 0}"

    def testNoSpeedKey(self):
        """Test move message that's missing a speed key."""
        self.socket.send("{cmd: move, opts: {not_speed: 50, angle: 0}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'speed' opt given"

    def testNoAngleKey(self):
        """Test move message that's missing an angle key."""
        self.socket.send("{cmd: move, opts: {speed: 50, not_angle: 0}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'angle' opt given"

    def testInvalidSpeedType(self):
        """Test move message with non-float speed key."""
        self.socket.send("{cmd: move, opts: {speed: invalid, angle: 0}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert speed to float"

    def testInvalidAngleType(self):
        """Test move message with non-float angle key."""
        self.socket.send("{cmd: move, opts: {speed: 50, angle: invalid}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert angle to float"

    def testInvalidSpeedValue(self):
        """Test move message with out of bounds speed value."""
        self.socket.send("{cmd: move, opts: {speed: 101, angle: 0}}")
        reply = self.socket.recv()
        assert reply == "Error: Speed is out of bounds", reply

    def testInvalidAngleValue(self):
        """Test move message with out of bounds angle value."""
        self.socket.send("{cmd: move, opts: {speed: 50, angle: 361}}")
        reply = self.socket.recv()
        assert reply == "Error: Angle is out of bounds", reply


class TestHandleRotate(unittest.TestCase):

    """Test rotate commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testValid(self):
        """Test rotate message that's perfectly valid."""
        self.socket.send("{cmd: rotate, opts: {speed: 100}}")
        reply = self.socket.recv()
        assert reply == "Success: {'speed': 100}"

    def testNoSpeedKey(self):
        """Test rotate message that's missing a speed key."""
        self.socket.send("{cmd: rotate, opts: {not_speed: 50}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'speed' opt given"

    def testInvalidSpeedType(self):
        """Test rotate message with non-float speed key."""
        self.socket.send("{cmd: rotate, opts: {speed: invalid}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert speed to float"

    def testInvalidSpeedValue(self):
        """Test rotate message with out of bounds speed value."""
        self.socket.send("{cmd: rotate, opts: {speed: 101}}")
        reply = self.socket.recv()
        assert reply == "Error: Rotate speed is out of bounds", reply


class TestHandleFire(unittest.TestCase):

    """Test fire command."""

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testValid(self):
        """Test fire message that's perfectly valid."""
        self.socket.send("{cmd: fire, opts: {}}")
        reply = self.socket.recv()
        assert reply == "Success: Fired"


class TestHandleAim(unittest.TestCase):

    """Test turrent aiming commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testValid(self):
        """Test aim message that's perfectly valid."""
        self.socket.send("{cmd: aim, opts: {y: 90, x: 90}}")
        reply = self.socket.recv()
        assert reply == "Success: {'y': 90, 'x': 90}"

    def testNoXKey(self):
        """Test aim message that's missing an x angle key."""
        self.socket.send("{cmd: aim, opts: {y: 90, not_x: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'x' opt given"

    def testNoYKey(self):
        """Test aim message that's missing a y angle key."""
        self.socket.send("{cmd: aim, opts: {not_y: 90, x: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'y' opt given"

    def testInvalidXType(self):
        """Test aim message with non-int x ange key."""
        self.socket.send("{cmd: aim, opts: {y: 90, x: invalid}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert x to int"

    def testInvalidYType(self):
        """Test aim message with non-int y angle key."""
        self.socket.send("{cmd: aim, opts: {y: invalid, x: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert y to int"

    def testInvalidXValue(self):
        """Test aim message with out of bounds x value."""
        self.socket.send("{cmd: aim, opts: {y: 90, x: 181}}")
        reply = self.socket.recv()
        assert reply == "Error: X angle is out of bounds", reply

    def testInvalidYValue(self):
        """Test aim message with out of bounds y value."""
        self.socket.send("{cmd: aim, opts: {y: 181, x: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: Y angle is out of bounds", reply


class TestHandleAdvanceDart(unittest.TestCase):

    """Test advance dart command."""

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testValid(self):
        """Test fire message that's perfectly valid."""
        self.socket.send("{cmd: advance_dart, opts: {}}")
        reply = self.socket.recv()
        assert reply == "Success: Advanced dart"


class TestHandleFireSpeed(unittest.TestCase):

    """Test rotate commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Load config
        config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = config["testing"]
        lib.set_testing(True)

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(config["server_port"])

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()
        lib.set_testing(self.orig_test_state)

    def testValid(self):
        """Test fire speed message that's perfectly valid."""
        self.socket.send("{cmd: fire_speed, opts: {speed: 100}}")
        reply = self.socket.recv()
        assert reply == "Success: {'speed': 100}"

    def testNoSpeedKey(self):
        """Test fire speed message that's missing a speed key."""
        self.socket.send("{cmd: fire_speed, opts: {not_speed: 50}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'speed' opt given"

    def testInvalidSpeedType(self):
        """Test fire speed message with non-int speed key."""
        self.socket.send("{cmd: fire_speed, opts: {speed: invalid}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert speed to int"

    def testInvalidSpeedValue(self):
        """Test fire speed message with out of bounds speed value."""
        self.socket.send("{cmd: fire_speed, opts: {speed: 101}}")
        reply = self.socket.recv()
        assert reply == "Error: Speed is out of bounds", reply
