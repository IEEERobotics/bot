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
    
    # Build ZMQ socket
    #context = zmq.Context()
    #api_sock = self.context.socket(zmq.REQ)

    #def __init__(self, api_addr):
    #    """"""
    #    self.api_addr = api_addr
    #    api_sock.connect(api_addr)
    #    print "Connected to server at {}".format(api_addr)

    def send_cmd(self, cmd, sock, opts=None):
        """Send generic commands to server.

        :param cmd: Value of 'cmd' key to send.
        :param opts: Value of 'opts' key to send.
        :param server: Server to send command to.
        :returns: Reply msg from server or None if server unknown.

        """
        # Build message
        msg = {}
        msg["cmd"] = cmd
        if opts is not None:
            msg["opts"] = opts

        # Send message to server and get reply
        sock.send_json(msg)
        reply = sock.recv_json()
        print "Reply: {}".format(reply)
        return reply
