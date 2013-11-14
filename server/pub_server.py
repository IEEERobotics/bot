#!/usr/bin/env python
"""Server for publishing data about the bot."""

import sys
import os
from time import sleep
import threading

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

new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path

import lib.lib as lib
import driver.mec_driver as md_mod
import gunner.wheel_gunner as wg_mod
import follower.follower as f_mod


class PubServer(threading.Thread):

    """Publish information about the status of the bot."""

    def __init__(self, context):
        """Override Thread.__init__, build ZMQ PUB socket."""
        # Call superclass __init__
        threading.Thread.__init__(self)

        # Unpack required objects from context
        self.gunner = context["gunner"]
        self.follower = context["follower"]
        self.driver = context["driver"]
        self.ir_hub = context["ir_hub"]

        # Load configuration and logger
        self.config = lib.load_config()
        self.logger = lib.get_logger()

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

    def run(self):
        """Override Thread.run. Execution starts here when thread is started."""
        while True:
            socks = dict(self.poller.poll(0))
            if self.topic_sock in socks:
                topic = self.topic_sock.recv_json()
                self.logger.info("New pub topic: {}".format(topic))
                reply = self.build_reply("Error", msg="Not yet implemented")
                self.topic_sock.send_json(reply)
                self.logger.warning("Adding topics not implemented")
            self.publish()

    def publish(self):
        """Publish information about bot."""
        self.pub_drive_motor_br_detail()
        self.pub_drive_motor_fr_detail()
        self.pub_drive_motor_bl_detail()
        self.pub_drive_motor_fl_detail()
        #self.pub_gun_motor_detail()
        self.pub_turret_detail()
        #self.pub_gun_speed()
        self.pub_turret_yaw()
        self.pub_turret_pitch()
        self.pub_drive_motor_br_speed()
        self.pub_drive_motor_fr_speed()
        self.pub_drive_motor_bl_speed()
        self.pub_drive_motor_fl_speed()
        self.pub_drive_motor_br_dir()
        self.pub_drive_motor_fr_dir()
        self.pub_drive_motor_bl_dir()
        self.pub_drive_motor_fl_dir()
        self.pub_drive_motor_br_vel()
        self.pub_drive_motor_fr_vel()
        self.pub_drive_motor_bl_vel()
        self.pub_drive_motor_fl_vel()
        self.pub_irs()
        sleep(1)

    def build_reply(self, status, result=None, msg=None):
        """Helper function for building standard replies.

        :param status: Exit status code ("Error"/"Success").
        :param result: Optional details of result (eg current speed).
        :param msg: Optional message (eg "Not implemented").
        :returns: A dict with status, result and msg.

        """
        if status != "Success" and status != "Error":
            self.logger.warn("Status is typically 'Success' or 'Error'")

        reply_msg = {}
        reply_msg["status"] = status
        if result is not None:
            reply_msg["result"] = result
        if msg is not None:
            reply_msg["msg"] = msg
        return reply_msg

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
