"""Functionally that should be inherited by bot-control clients."""

import sys

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

import lib.lib as lib


class Client(object):

    """Parent class for clients that control the bot."""

    def __init__(self):
        """Get logger and config, connect to server.

        Note that this constructor supports building request or subscribe
        type clients, and will build the appropriate socket type and
        connect to the appropriate server addressed based on that param.
        The default behavior is to build a request client.

        :param client_type: Type of client to built ("request" or "subscribe").
        :type client_type: string

        """
        # Get logger
        self.logger = lib.get_logger()

        # Get config
        self.config = lib.load_config()

        # Build ZMQ socket and connect to server
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REQ)
        self.server_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_host"],
            port=self.config["server_port"])
        self.sock.connect(self.server_addr)
        self.logger.info("Connected to server at {}".format(
            self.server_addr))

        # Build ZMQ subscribe socket for PubServer
        self.sub_sock = self.context.socket(zmq.SUB)
        self.sub_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_host"],
            port=self.config["pub_server_pub_port"])
        self.sub_sock.connect(self.sub_addr)
        self.logger.info("Connected to server at {}".format(
            self.sub_addr))

         # Build ZMQ request socket for PubServer
        self.topic_sock = self.context.socket(zmq.REQ)
        self.topic_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_host"],
            port=self.config["pub_server_topic_port"])
        self.topic_sock.connect(self.topic_addr)
        self.logger.info("Connected to server at {}".format(
            self.topic_addr))

    def __str__(self):
        """Build human-readable representation of client.

        :returns: Human-readable representation of client, including socket.

        """
        return "Client connected to {}".format(self.sock)

    def cleanUp(self):
        """Tear down ZMQ socket."""
        self.sock.close()
        self.sub_sock.close()
        self.topic_sock.close()
        self.context.term()
        self.logger.info("Disconnected from server")

    def send_cmd(self, cmd, opts=None, server="ControlServer"):
        """Send generic commands to server.

        :param cmd: Value of 'cmd' key to send.
        :param opts: Value of 'opts' key to send.
        :param server: Server to send command to.
        :returns: True for success, False for failure.

        """
        # Build message
        msg = {}
        msg["cmd"] = cmd
        if opts is not None:
            msg["opts"] = opts
        else:
            msg["opts"] = {}

        # Send message to appropriate server
        if server == "ControlServer":
            self.logger.info("Sending to ControlServer: {}".format(msg))
            self.sock.send_json(msg)
            reply = self.sock.recv_json()
        elif server == "PubServer":
            self.logger.info("Sending to PubServer: {}".format(msg))
            self.topic_sock.send_json(msg)
            reply = self.topic_sock.recv_json()
        else:
            self.logger.warning("Unknown server: {}".format(server))
            return False

        # Handle reply
        if reply["status"] == "Success":
            self.logger.info("Reply: {}".format(reply))
            return True
        else:
            self.logger.warn("Reply: {}".format(reply))
            return False

    def send_aim(self, pitch, yaw):
        """Aim turret to given pitch and yaw angles.

        :param pitch: Yaw angle to aim turret (0-180).
        :param yaw: Yaw angle to aim turret (0-180).
        :returns: True for success, False for failure.

        """
        cmd = "aim"
        opts = {}
        opts["pitch"] = pitch
        opts["yaw"] = yaw
        return self.send_cmd(cmd, opts)

    def send_fire_speed(self, speed):
        """Send speed to fire dart to server.

        :param speed: Speed to fire as percentage of max (0-100).
        :returns: True for success, False for failure.

        """
        cmd = "fire_speed"
        opts = {}
        opts["speed"] = speed
        return self.send_cmd(cmd, opts)

    def send_fire(self):
        """Send command to push dart into firing wheels."""
        cmd = "fire"
        return self.send_cmd(cmd)

    def send_auto_fire(self):
        """Send command to fire dart using autonomous methods.

        :returns: True for success, False for failure.

        """
        cmd = "auto_fire"
        return self.send_cmd(cmd)

    def send_fwd_strafe_turn(self, fwd, strafe, turn):
        """Send move command with fwd, strafe and turn speeds to server.

        :param fwd: Forward speed component of move command.
        :param strafe: Strafe speed component of move command.
        :param turn: Turn speed component of move command.
        :returns: True for success, False for failure.

        """
        cmd = "fwd_strafe_turn"
        opts = {}
        opts["fwd"] = fwd
        opts["strafe"] = strafe
        opts["turn"] = turn
        return self.send_cmd(cmd, opts)

    def send_move(self, speed, angle):
        """Send command to move at given speed/angle to server.

        :param speed: Seed to move as percent of max (0-100).
        :param angle: Angle to move (0-360).
        :returns: True for success, False for failure.

        """
        cmd = "move"
        opts = {}
        opts["speed"] = speed
        opts["angle"] = angle
        return self.send_cmd(cmd, opts)

    def send_rotate(self, speed):
        """Send command to rotate the bot at the give speed.

        :param speed: Rotation speed (-100 to 100, positive counterclockwise).
        :returns: True for success, False for failure.

        """
        cmd = "rotate"
        opts = {}
        opts["speed"] = speed
        return self.send_cmd(cmd, opts)

    def send_pub_add(self, topic):
        """Send command to add a new topic for PubServer to publish.

        :param topic: Topic that PubServer should start publishing.
        :type topic: string

        """
        cmd = "pub_add"
        opts = {}
        opts["topic"] = topic
        return self.send_cmd(cmd, opts, server="PubServer")

    def send_pub_del(self, topic):
        """Send command to delete topic that PubServer is publishing.

        :param topic: Topic that PubServer should stop publishing.
        :type topic: string

        """
        cmd = "pub_del"
        opts = {}
        opts["topic"] = topic
        return self.send_cmd(cmd, opts, server="PubServer")

    def send_die(self):
        """Send die command to server.

        :returns: True for success, False for failure.

        """
        cmd = "die"
        return self.send_cmd(cmd)
