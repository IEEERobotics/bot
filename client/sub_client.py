"""Subscribe to data published by the bot."""

import sys
from pprint import pprint
from time import time

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

import client


class SubClient(client.Client):

    """Use ZMQ SUB socket to get information about the bot."""

    def __init__(self, sub_addr, topic_addr):
        """Get logger and config, build subscribe socket and set topics."""
        # Call superclass
        super(SubClient, self).__init__()

        # Build ZMQ subscribe socket for PubServer
        self.context = zmq.Context()
        self.sub_sock = self.context.socket(zmq.SUB)
        self.sub_addr = sub_addr
        self.sub_sock.connect(self.sub_addr)
        print "SubClient subscribed to PubServer at {}".format(
            self.sub_addr)

        # Build ZMQ request socket for PubServer
        self.topic_sock = self.context.socket(zmq.REQ)
        self.topic_addr = topic_addr
        self.topic_sock.connect(self.topic_addr)
        print "SubClient can set PubServer topics at {}".format(
            self.topic_addr)

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
                return

    def add_topic(self, topic):
        """"""
        # Set our sub socket to listen for the new topic
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, topic)

        # Tell the server to start publishing the new topic
        cmd = "pub_add"
        opts = {}
        opts["topic"] = topic
        return self.send_cmd(cmd, self.topic_sock, opts)

    def del_topic(self, topic):
        """"""
        # Tell sub socket to stop listening to the given topic
        self.sub_sock.setsockopt(zmq.UNSUBSCRIBE, topic)

        # Tell the server to stop publishing the given topic
        cmd = "pub_del"
        opts = {}
        opts["topic"] = topic
        return self.send_cmd(cmd, self.topic_sock, opts)

    def ping(self):
        """Ping the remote PubServer.

        :returns: Reply messages and reply time in seconds.

        """
        cmd = "ping"
        start = time()
        reply = self.send_cmd(cmd, self.topic_sock)
        reply_time = time() - start
        return reply, reply_time
