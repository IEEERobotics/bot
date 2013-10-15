"""Code that bot-control clients can inherit"""

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
        self.sock.close()
        self.context.term()
        self.logger.info("Disconnected from server")
