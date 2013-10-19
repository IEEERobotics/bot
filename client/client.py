"""Code that bot-control clients can inherit"""

import sys

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

import lib.lib as lib
import server.server as server

class Client(object):

    """Parent class for clients that control the bot."""

    def __init__(self):
        """"""
        # Get logger
        self.logger = lib.get_logger()

        # Get config
        self.config = lib.load_config()

        # Build ZMQ socket and connect to server
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REQ)
        self.sock.connect(self.config["server_port"])
        self.logger.info("Connected to control server at {}".format(
                                            self.config["server_port"]))


    def __str__(self):
        """Build human-readable representation of client."""
        return "Client connected to {}".format(self.sock)

    def cleanUp(self):
        """Tear down ZMQ socket."""
        self.sock.close()
        self.context.term()
        self.logger.info("Disconnected from server")

    def send_cmd(self, cmd, opts):
        """Send genetic commands to server.

        :param cmd: Value of 'cmd' key to send.
        :param opts: Value of 'opts' key to send.
        :returns: True for success, False for failure.

        """

        self.sock.send("{{cmd: {}, opts: {}}}".format(cmd, opts))
        reply = self.sock.recv()
        if "Success" in reply:
            self.logger.info("{}".format(reply))
            return True
        else:
            self.logger.warn("{}".format(reply))
            return False

    def send_aim(self, x, y):
        """Aim turret to given X and Y angles.

        :param x: X angle to aim turret (0-180).
        :param y: Y angle to aim turret (0-180).
        :returns: True for success, False for failure.

        """
        cmd = "aim"
        opts = "{{y: {}, x: {}}}".format(x, y)
        return self.send_cmd(cmd, opts)

    def send_fire_speed(self, speed):
        """"""
        cmd = "fire_speed"
        opts = "{{speed: {}}}".format(speed)
        return self.send_cmd(cmd, opts)

    def send_fire(self):
        """Send command to fire dart."""
        cmd = "fire"
        opts = "{}"
        return self.send_cmd(cmd, opts)

    def send_die(self):
        """Send die command to server."""
        cmd = "die"
        opts = "{}"
        return self.send_cmd(cmd, opts)
