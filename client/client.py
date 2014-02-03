"""Functionally that should be inherited by bot clients."""

import sys

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

import lib.lib as lib


class Client(object):

    """Parent class for clients."""

    def __init__(self):
        """Build ZMQ context."""
        self.context = zmq.Context()
    
    def clean_up(self, sock):
        """Tear down ZMQ socket."""
        sock.sock.close()
        self.context.term()

