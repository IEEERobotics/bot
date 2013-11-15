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
        super(SubClient, self).__init__()
        self.set_topics()

    def set_topics(self):
        """Subscribe to a set of topics.

        Note that this will be updated to be smarter.

        """
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_detail")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_detail")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_detail")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_detail")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "gun_motor_detail")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "turret_detail")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "gun_speed")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "turret_yaw")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "turret_pitch")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_speed")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_speed")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_speed")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_speed")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_dir")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_dir")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_dir")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_dir")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_br_vel")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fr_vel")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_bl_vel")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "drive_motor_fl_vel")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "ir_front")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "ir_back")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "ir_left")
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, "ir_right")

    def print_msgs(self):
        """Print all messages from server."""
        while True:
            try:
                pprint(self.sub_sock.recv())
            except KeyboardInterrupt:
                print "Closing SubClient"
                sys.exit(0)
