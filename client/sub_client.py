"""Subscribe to data published by the bot."""

import sys
from pprint import pprint

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

import client


class SubClient(client.Client):

    """Use ZMQ SUB socket to get information about the bot."""

    def __init__(self):
        """Get logger and config, build subscribe socket and set topics."""
        super(SubClient, self).__init__("subscribe")
        self.set_topics()

    def set_topics(self):
        """Subscribe to a set of topics.

        Note that this will be updated to be smarter.

        """
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_detail")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_detail")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_detail")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_detail")
        self.sock.setsockopt(zmq.SUBSCRIBE, "gun_motor_detail")
        self.sock.setsockopt(zmq.SUBSCRIBE, "turret_detail")
        self.sock.setsockopt(zmq.SUBSCRIBE, "gun_speed")
        self.sock.setsockopt(zmq.SUBSCRIBE, "turret_yaw")
        self.sock.setsockopt(zmq.SUBSCRIBE, "turret_pitch")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_speed")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_speed")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_speed")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_speed")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_dir")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_dir")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_dir")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_dir")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_vel")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_vel")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_vel")
        self.sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_vel")
        self.sock.setsockopt(zmq.SUBSCRIBE, "ir_front")
        self.sock.setsockopt(zmq.SUBSCRIBE, "ir_back")
        self.sock.setsockopt(zmq.SUBSCRIBE, "ir_left")
        self.sock.setsockopt(zmq.SUBSCRIBE, "ir_right")

    def print_msgs(self):
        """Print all messages from server."""
        while True:
            try:
                pprint(self.sock.recv())
            except KeyboardInterrupt:
                print "Closing SubClient"
                sys.exit(0)
