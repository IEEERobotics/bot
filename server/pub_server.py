#!/usr/bin/env python
"""Server for publishing data about the bot."""

import sys
import os
import threading
from inspect import getmembers, ismethod

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path

import lib.lib as lib
import server.server as server


class PubServer(threading.Thread, server.Server):

    """Publish information about the status of the bot.

    Note that by default, there are no topics set to publish. Clients can
    send topics to the REP ZMQ socket owned by PubServer to set new topics.

    """

    publisher_prefix = "pub_"

    def __init__(self, context):
        """Override Thread.__init__, build ZMQ PUB socket."""
        # Call superclass __init__ methods
        threading.Thread.__init__(self)
        server.Server.__init__(self)

        # Unpack required objects from context
        self.gunner = context["gunner"]
        self.follower = context["follower"]
        self.driver = context["driver"]
        self.ir_hub = context["ir_hub"]

        # Build ZMQ publisher socket
        self.context = zmq.Context()
        self.pub_sock = self.context.socket(zmq.PUB)
        self.pub_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["pub_server_pub_port"])
        self.pub_sock.bind(self.pub_addr)

        # Build ZMQ reply socket for setting topics
        self.topic_sock = self.context.socket(zmq.REP)
        self.topic_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["pub_server_topic_port"])
        self.topic_sock.bind(self.topic_addr)

        # Build poller and register topic socket
        self.poller = zmq.Poller()
        self.poller.register(self.topic_sock, zmq.POLLIN)

        # Create topic -> publisher methods mapping (dict)
        self.publishers = dict()
        for name, method in getmembers(self, ismethod):
            if name.startswith(self.publisher_prefix):
                topic = name.replace(self.publisher_prefix, "", 1)
                self.publishers[topic] = method
        self.logger.info("{} publishers registered".format(len(self.publishers)))

        # Topics that will be published by default.
        self.topics = []

    def run(self):
        """Check for new publisher topics, add them, publish topics.

        Note that this overrides Thread.run and is the entry point when
        starting this thread.

        """
        while True:
            # Check if there's a new topic to add, block for 1 sec
            socks = dict(self.poller.poll(1000))

            # Check if there's a new topic add/del message
            if self.topic_sock in socks:
                msg = self.topic_sock.recv_json()
                reply = self.on_message(msg)
                self.logger.info(reply)
                self.topic_sock.send_json(reply)

            # Publish topics
            self.publish()

    def publish(self):
        """Publish information about bot."""
        for topic in self.topics:
            self.publishers[topic]()

    def handle_pub_add(self, opts):
        """Parse message to get topic, add new topic.

        :param msg: Opts received via ZMQ, including topic.
        :type msg: dict
        :returns: Reply message to send out ZMQ socket.

        """
        try:
            topic = opts["topic"]
            assert type(topic) is str
        except KeyError:
            self.build_reply("Error", "No 'topic' key")
        except AssertionError:
            self.build_reply("Error", "Topic is not a string")

        # TODO: Assert that topic is valid

        if topic in self.topics:
            reply_msg = "Topic already set: {}".format(topic)
            return self.build_reply("Error", msg=reply_msg)
        else:
            self.topics.append(topic)
            reply_msg = "Topic added: {}".format(topic)
            return self.build_reply("Success", msg=reply_msg)

    def handle_pub_del(self, opts):
        """Parse message to get topic, delete given topic.

        :param msg: Opts received via ZMQ, including topic.
        :type msg: dict
        :returns: Reply message to send out ZMQ socket.

        """
        try:
            topic = opts["topic"]
            assert type(topic) is str
        except KeyError:
            self.build_reply("Error", "No 'topic' key")
        except AssertionError:
            self.build_reply("Error", "Topic is not a string")

        if topic in self.topics:
            self.topics.remove(topic)
            reply_msg = "Topic deleted: {}".format(topic)
            return self.build_reply("Success", msg=reply_msg)
        else:
            reply_msg = "Topic not set: {}".format(topic)
            return self.build_reply("Error", msg=reply_msg)

    def pub_drive_motor_br_detail(self):
        """Publish all info about back right drive motor."""
        br_motor = self.driver.motors["back_right"]
        self.pub_sock.send("drive_motor_br_detail {}".format(br_motor))

    def pub_drive_motor_fr_detail(self):
        """Publish all info about front right drive motor."""
        fr_motor = self.driver.motors["front_right"]
        self.pub_sock.send("drive_motor_fr_detail {}".format(fr_motor))

    def pub_drive_motor_bl_detail(self):
        """Publish all info about back left drive motor."""
        bl_motor = self.driver.motors["back_left"]
        self.pub_sock.send("drive_motor_bl_detail {}".format(bl_motor))

    def pub_drive_motor_fl_detail(self):
        """Publish all info about front left drive motor."""
        fl_motor = self.driver.motors["front_left"]
        self.pub_sock.send("drive_motor_fl_detail {}".format(fl_motor))

    # TODO: Add back once capes are installed
    #def pub_gun_motor_detail(self):
    #    """Publish all info about gun motors"""
    #    for motor in self.gunner.motors:
    #        self.pub_sock.send("gun_motor_detail {}".format(motor))

    def pub_turret_detail(self):
        """Publish all info about turret servos."""
        self.pub_sock.send("turret_detail {}".format(self.gunner.turret))

    # TODO: Add back once capes are installed
    #def pub_gun_speed(self):
    #    """Publish speed of gun motors."""
    #    self.pub_sock.send("gun_speed {}".format(self.gunner.wheel_speed))

    def pub_turret_yaw(self):
        """Publish yaw angle of turret."""
        self.pub_sock.send("turret_yaw {}".format(self.gunner.turret.yaw))

    def pub_turret_pitch(self):
        """Publish pitch angle of turret."""
        self.pub_sock.send("turret_pitch {}".format(self.gunner.turret.pitch))

    def pub_drive_motor_br_speed(self):
        """Publish speed of back right drive motor."""
        speed = self.driver.motors["back_right"].speed
        self.pub_sock.send("drive_motor_br_speed {}".format(speed))

    def pub_drive_motor_fr_speed(self):
        """Publish speed of front right drive motor."""
        speed = self.driver.motors["front_right"].speed
        self.pub_sock.send("drive_motor_fr_speed {}".format(speed))

    def pub_drive_motor_bl_speed(self):
        """Publish speed of back left drive motor."""
        speed = self.driver.motors["back_left"].speed
        self.pub_sock.send("drive_motor_bl_speed {}".format(speed))

    def pub_drive_motor_fl_speed(self):
        """Publish speed of front left drive motor."""
        speed = self.driver.motors["front_left"].speed
        self.pub_sock.send("drive_motor_fl_speed {}".format(speed))

    def pub_drive_motor_br_dir(self):
        """Publish direction of back right drive motor."""
        direction = self.driver.motors["back_right"].direction
        self.pub_sock.send("drive_motor_br_dir {}".format(direction))

    def pub_drive_motor_fr_dir(self):
        """Publish direction of front right drive motor."""
        direction = self.driver.motors["front_right"].direction
        self.pub_sock.send("drive_motor_fr_dir {}".format(direction))

    def pub_drive_motor_bl_dir(self):
        """Publish direction of back left drive motor."""
        direction = self.driver.motors["back_left"].direction
        self.pub_sock.send("drive_motor_bl_dir {}".format(direction))

    def pub_drive_motor_fl_dir(self):
        """Publish direction of front left drive motor."""
        direction = self.driver.motors["front_left"].direction
        self.pub_sock.send("drive_motor_fl_dir {}".format(direction))

    def pub_drive_motor_br_vel(self):
        """Publish velocity of back right drive motor."""
        velocity = self.driver.motors["back_right"].velocity
        self.pub_sock.send("drive_motor_br_vel {}".format(velocity))

    def pub_drive_motor_fr_vel(self):
        """Publish velocity of front right drive motor."""
        velocity = self.driver.motors["front_right"].velocity
        self.pub_sock.send("drive_motor_fr_vel {}".format(velocity))

    def pub_drive_motor_bl_vel(self):
        """Publish velocity of back left drive motor."""
        velocity = self.driver.motors["back_left"].velocity
        self.pub_sock.send("drive_motor_bl_vel {}".format(velocity))

    def pub_drive_motor_fl_vel(self):
        """Publish velocity of front left drive motor."""
        velocity = self.driver.motors["front_left"].velocity
        self.pub_sock.send("drive_motor_fl_vel {}".format(velocity))

    def pub_irs(self):
        """Publish IR readings from all sensors."""
        reading = self.ir_hub.read_all_arrays()
        self.pub_sock.send("ir_front {}".format(reading["front"]))
        self.pub_sock.send("ir_back {}".format(reading["back"]))
        self.pub_sock.send("ir_left {}".format(reading["left"]))
        self.pub_sock.send("ir_right {}".format(reading["right"]))
