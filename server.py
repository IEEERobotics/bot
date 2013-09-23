#!/usr/bin/env python
"""Lightweight server to start/stop controllers."""

import sys
from time import sleep

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

try:
    import yaml
except ImportError, err:
    sys.stderr.write("ERROR: {}. Try installing python-yaml.\n".format(err))
    raise

import lib.lib as lib


class Server(object):

    """Start/stop controllers when instructed via server port."""

    def __init__(self):
        """Build logger, set ZMQ to listen on server port."""
        # TODO(dfarrell07): Build server logger, don't reuse bot logger

        # Load and store configuration
        self.config = lib.load_config()

        # Listen for incoming requests
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.config["server_port"])
        #print "Server bound to {}".format(self.config["server_port"])

    def listen(self):
        """Listen for messages, pass them off to be handled and send reply."""
        while True:
            #print "Listening for message..."
            msg_raw = self.socket.recv()
            #print "Received message: {}".format(msg_raw)

            reply_msg = self.handle_msg(msg_raw)
            print reply_msg
            self.socket.send(reply_msg)

    def handle_msg(self, msg_raw):
        """Confirm message format and take appropriate action.

        :param msg_raw: Raw message string received by ZMQ.
        :type msg_raw: string
        :returns: Success or failure message, plus description.

        """
        try:
            msg = dict(yaml.safe_load(msg_raw))
            cmd = msg["cmd"]
            assert type(cmd) is str
        except ValueError:
            return "Error: Unable to convert message to dict"
        except KeyError:
            return "Error: No 'cmd' key given"
        except AssertionError:
            return "Error: Key 'cmd' is not a string"

        try:
            opts = msg["opts"]
            assert type(opts) is dict
        except KeyError:
            return "Error: No 'opts' key given"
        except AssertionError:
            return "Error: Key 'opts' is not a dict"

        if msg["cmd"] == "move":
            self.handle_move(opts)
        elif msg["cmd"] == "die":
            #print "Success: Received message to die. Bye!"
            self.socket.send("Success: Received message to die. Bye!")
            sys.exit(0)
        else:
            return "Error: Unknown cmd {}".format(cmd)

    def handle_move(self, opts):
        # Validate speed option
        try:
            speed = float(opts["speed"])
        except KeyError:
            return "Error: No 'speed' opt given"
        except ValueError:
            return "Error: Could not convert speed to float"
        # Validate angle option
        try:
            angle = float(opts["angle"])
        except KeyError:
            return "Error: No 'angle' opt given"
        except ValueError:
            return "Error: Could not convert angle to float"
        # Make call to driver
        try:
            self.driver.move(speed=speed, angle=angle)
        except Exception as e:
            return "Error: {}".format(e)


if __name__ == "__main__":
    server = Server()
    server.listen()
