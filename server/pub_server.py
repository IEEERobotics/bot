"""Server for publishing data about the bot."""

import sys
import os
import threading
from time import sleep

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

import lib.lib as lib


class PubServer(threading.Thread):

    """Publish information about the status of the bot.

    Note that by default, there are no topics set to publish.

    """

    # How often topics are published, in seconds.
    pub_delay = 1

    def __init__(self, systems):
        """Override Thread.__init__, build ZMQ PUB socket.

        :param systems: Objects that own resources and drive functionally.
        :type systems: dict

        """
        # Call superclass __init__ methods
        threading.Thread.__init__(self)

        # Load configuration and logger
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        # Unpack required objects from systems
        self.gunner = systems["gunner"]
        self.follower = systems["follower"]
        self.driver = systems["driver"]
        self.ir_hub = systems["ir_hub"]

        # Build ZMQ publisher socket
        self.context = zmq.Context()
        self.pub_sock = self.context.socket(zmq.PUB)
        self.pub_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["pub_server_port"])
        self.pub_sock.bind(self.pub_addr)

        # Mapping of published topics to methods that give their value
        # I know some of these lines are too long. Fuck it, it's clean code.
        self.topics = {
            "drive_motor_detail_br": self.driver.motors["back_right"].__str__,
            "drive_motor_detail_fr": self.driver.motors["front_right"].__str__,
            "drive_motor_detail_bl": self.driver.motors["back_left"].__str__,
            "drive_motor_detail_fl": self.driver.motors["front_left"].__str__,
            "drive_motor_vel_br": self.driver.motors["back_right"].get_velocity,
            "drive_motor_vel_fr": self.driver.motors["front_right"].get_velocity,
            "drive_motor_vel_bl": self.driver.motors["back_left"].get_velocity,
            "drive_motor_vel_fl": self.driver.motors["front_left"].get_velocity,
            "drive_motor_speed_br": self.driver.motors["back_right"].get_speed,
            "drive_motor_speed_fr": self.driver.motors["front_right"].get_speed,
            "drive_motor_speed_bl": self.driver.motors["back_left"].get_speed,
            "drive_motor_speed_fl": self.driver.motors["front_left"].get_speed,
            "drive_motor_dir_br": self.driver.motors["back_right"].get_direction,
            "drive_motor_dir_fr": self.driver.motors["front_right"].get_direction,
            "drive_motor_dir_bl": self.driver.motors["back_left"].get_direction,
            "drive_motor_dir_fl": self.driver.motors["front_left"].get_direction,
            "turret_detail": self.gunner.turret.__str__,
            "turret_yaw": self.gunner.turret.get_yaw,
            "turret_pitch": self.gunner.turret.get_pitch,
            "ir": self.ir_hub.read_all
        }

    def run(self):
        """Entry point for thread, just publishes topics.

        Note that this overrides Thread.run and is the entry point when
        starting this thread.

        """
        while True:
            # Publish topics
            sleep(self.pub_delay)
            self.publish()

    def publish(self):
        """Publish information about bot."""
        for topic_name, topic_val in self.topics.iteritems():
            self.pub_sock.send("{} {}".format(topic_name, topic_val()))
