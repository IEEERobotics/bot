"""Functionally that should be inherited by bot-control clients."""

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
        """Get logger and config, connect to server."""
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
        """Build human-readable representation of client.

        :returns: Human-readable representation of client, including socket.

        """
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
            self.logger.info("Server reply: {}".format(reply))
            return True
        else:
            self.logger.warn("Server reply: {}".format(reply))
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
        """Send speed to fire dart to server.

        :param speed: Speed to fire as percentage of max (0-100).
        :returns: True for success, False for failure.

        """
        cmd = "fire_speed"
        opts = "{{speed: {}}}".format(speed)
        return self.send_cmd(cmd, opts)

    def send_fire(self):
        """Send command to fire dart.

        :returns: True for success, False for failure.

        """
        cmd = "fire"
        opts = "{}"
        return self.send_cmd(cmd, opts)

    def send_fwd_strafe_turn(self, fwd, strafe, turn):
        """Send move command with fwd, strafe and turn speeds to server.

        :param fwd: Forward speed component of move command.
        :param strafe: Strafe speed component of move command.
        :param turn: Turn speed component of move command.
        :returns: True for success, False for failure.

        """
        cmd = "fwd_strafe_turn"
        opts = "{{fwd: {}, strafe: {}, turn: {}}}".format(fwd, strafe, turn)
        return self.send_cmd(cmd, opts)

    def send_move(self, speed, angle):
        """Send command to move at given speed/angle to server.

        :param speed: Seed to move as percent of max (0-100).
        :param angle: Angle to move (0-360).
        :returns: True for success, False for failure.

        """
        cmd = "move"
        opts = "{{speed: {}, angle: {}}}".format(speed, angle)
        return self.send_cmd(cmd, opts)

    def send_rotate(self, speed):
        """Send command to rotate the bot at the give speed.

        :param speed: Rotation speed (-100 to 100, positive counterclockwise).
        :returns: True for success, False for failure.

        """
        cmd = "rotate"
        opts = "{{speed: {}}}".format(speed)
        return self.send_cmd(cmd, opts)

    def send_die(self):
        """Send die command to server.

        :returns: True for success, False for failure.

        """
        cmd = "die"
        opts = "{}"
        return self.send_cmd(cmd, opts)
