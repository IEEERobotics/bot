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
    import server as server_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestHandleMessage(test_bot.TestBot):

    """Basic tests handle message method."""

    def setUp(self):
        """Build server and connect to it."""
        # Run general bot test setup
        super(TestHandleMessage, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_connect_addr = "{protocol}://{host}:{port}".format(
                                    protocol=self.config["server_protocol"],
                                    host=self.config["server_host"],
                                    port=self.config["server_port"])
        self.socket.connect(self.server_connect_addr)

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestHandleMessage, self).tearDown()

    def testInvalidMsgType(self):
        """Test sending a non-JSON message."""
        self.socket.send("not_json")
        reply = self.socket.recv_json()
        assert reply["status"] == "Error"
        assert reply["msg"] == "Non-JSON message"

    def testInvalidCmdKey(self):
        """Test sending a message without a valid cmd key."""
        msg = {}
        msg["not_cmd"] = "move"
        self.socket.send_json(msg)
        reply = self.socket.recv_json()
        assert reply["status"] == "Error"
        assert reply["msg"] == "No 'cmd' key given"

    def testInvalidOptsKey(self):
        """Test sending a message without a valid opts key."""
        msg = {}
        msg["cmd"] = "move"
        msg["not_opts"] = {}
        self.socket.send_json(msg)
        reply = self.socket.recv_json()
        assert reply["status"] == "Error"
        assert reply["msg"] == "opts key required for this cmd"

    def testInvalidCmdValue(self):
        """Test sending a message with an invalid cmd value."""
        msg = {}
        msg["cmd"] = "wrong_cmd"
        self.socket.send_json(msg)
        reply = self.socket.recv_json()
        assert reply["status"] == "Error"
        assert reply["msg"] == "Unknown cmd: wrong_cmd"


@unittest.skip("Not yet updated to work with JSON server")
class TestHandleFwdStrafeTurn(test_bot.TestBot):

    """Test fwd, strafe and turn commands.

    TODO: More test cases.

    """

    def setUp(self):
        """Build server and connect to it."""
        # Run general bot test setup
        super(TestHandleFwdStrafeTurn, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_connect_addr = "{protocol}://{host}:{port}".format(
                                    protocol=self.config["server_protocol"],
                                    host=self.config["server_host"],
                                    port=self.config["server_port"])
        self.socket.connect(self.server_connect_addr)

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestHandleFwdStrafeTurn, self).tearDown()

    def testValid(self):
        """Test fwd_strafe_turn message that's perfectly valid."""
        self.socket.send("{cmd: fwd_strafe_turn, " + \
                         "opts: {fwd: 50, turn: 0, strafe: 0}}")
        reply = self.socket.recv()
        assert reply == "Success: {'fwd': 50, 'turn': 0, 'strafe': 0}", reply


@unittest.skip("Not yet updated to work with JSON server")
class TestHandleMove(test_bot.TestBot):

    """Test move commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Run general bot test setup
        super(TestHandleMove, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_connect_addr = "{protocol}://{host}:{port}".format(
                                    protocol=self.config["server_protocol"],
                                    host=self.config["server_host"],
                                    port=self.config["server_port"])
        self.socket.connect(self.server_connect_addr)

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestHandleMove, self).tearDown()

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


@unittest.skip("Not yet updated to work with JSON server")
class TestHandleRotate(test_bot.TestBot):

    """Test rotate commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Run general bot test setup
        super(TestHandleRotate, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_connect_addr = "{protocol}://{host}:{port}".format(
                                    protocol=self.config["server_protocol"],
                                    host=self.config["server_host"],
                                    port=self.config["server_port"])
        self.socket.connect(self.server_connect_addr)

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestHandleRotate, self).tearDown()

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


@unittest.skip("Not yet updated to work with JSON server")
class TestHandleAutoFire(test_bot.TestBot):

    """Test auto_fire command."""

    def setUp(self):
        """Build server and connect to it."""
        # Run general bot test setup
        super(TestHandleAutoFire, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_connect_addr = "{protocol}://{host}:{port}".format(
                                    protocol=self.config["server_protocol"],
                                    host=self.config["server_host"],
                                    port=self.config["server_port"])
        self.socket.connect(self.server_connect_addr)

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestHandleAutoFire, self).tearDown()

    def testValid(self):
        """Test auto_fire message that's perfectly valid."""
        self.socket.send("{cmd: auto_fire, opts: {}}")
        reply = self.socket.recv()
        assert reply == "Success: Fired", reply


@unittest.skip("Not yet updated to work with JSON server")
class TestHandleAim(test_bot.TestBot):

    """Test turret aiming commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Run general bot test setup
        super(TestHandleAim, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_connect_addr = "{protocol}://{host}:{port}".format(
                                    protocol=self.config["server_protocol"],
                                    host=self.config["server_host"],
                                    port=self.config["server_port"])
        self.socket.connect(self.server_connect_addr)

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestHandleAim, self).tearDown()

    def testValid(self):
        """Test aim message that's perfectly valid."""
        self.socket.send("{cmd: aim, opts: {pitch: 90, yaw: 90}}")
        reply = self.socket.recv()
        assert reply == "Success: {'yaw': 90, 'pitch': 90}", reply

    def testNoYawKey(self):
        """Test aim message that's missing an yaw angle key."""
        self.socket.send("{cmd: aim, opts: {pitch: 90, not_yaw: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'yaw' opt given"

    def testNoPitchKey(self):
        """Test aim message that's missing a y angle key."""
        self.socket.send("{cmd: aim, opts: {not_pitch: 90, yaw: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: No 'pitch' opt given"

    def testInvalidYawType(self):
        """Test aim message with non-int yaw angle key."""
        self.socket.send("{cmd: aim, opts: {pitch: 90, yaw: invalid}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert yaw to int"

    def testInvalidPitchType(self):
        """Test aim message with non-int pitch angle key."""
        self.socket.send("{cmd: aim, opts: {pitch: invalid, yaw: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: Could not convert pitch to int"

    def testInvalidYawValue(self):
        """Test aim message with out of bounds yaw value."""
        self.socket.send("{cmd: aim, opts: {pitch: 90, yaw: 181}}")
        reply = self.socket.recv()
        assert reply == "Error: Yaw angle is out of bounds", reply

    def testInvalidPitchValue(self):
        """Test aim message with out of bounds pitch value."""
        self.socket.send("{cmd: aim, opts: {pitch: 181, yaw: 90}}")
        reply = self.socket.recv()
        assert reply == "Error: Pitch angle is out of bounds", reply

@unittest.skip("Not yet implemented")
class TestHandleFireSpeed(test_bot.TestBot):

    """Test rotate commands."""

    def setUp(self):
        """Build server and connect to it."""
        # Run general bot test setup
        super(TestHandleFireSpeed, self).setUp()

        # Build server. Arg is testing or not.
        self.server = Popen(["./server/server.py", "True"])

        # Build socket and connect to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_connect_addr = "{protocol}://{host}:{port}".format(
                                    protocol=self.config["server_protocol"],
                                    host=self.config["server_host"],
                                    port=self.config["server_port"])
        self.socket.connect(self.server_connect_addr)

    def tearDown(self):
        """Kill server, restore testing flag state in config file."""
        self.socket.close()
        self.context.term()
        self.server.kill()

        # Run general bot test tear down
        super(TestHandleFireSpeed, self).tearDown()

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
