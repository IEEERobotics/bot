#!/usr/bin/env python
"""Server for publishing data about the bot."""

import sys
import os
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

new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path

import lib.lib as lib
import driver.mec_driver as md_mod
import gunner.wheel_gunner as wg_mod
import follower.follower as f_mod


class PubServer(object):

    """Publish information about the status of the bot."""

    def __init__(self, testing=None):
        """Build all main bot objects, build ZMQ PUB socket."""
        # Load configuration and logger
        self.config = lib.load_config()
        self.logger = lib.get_logger()

        # Testing flag will cause objects to run on simulated hardware
        if testing == "True":
            self.logger.info("PubServer will build bot objects in test mode")
            lib.set_testing(bool(testing))
        elif testing == "False":
            self.logger.info("PubServer will build objects in non-test mode")
            lib.set_testing(bool(testing))
        else:
            self.logger.info("Defaulting to config testing flag: {}".format(
                                                    self.config["testing"]))
            lib.set_testing(self.config["testing"])

        # Build ZMQ publisher socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.server_bind_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["pub_server_port"])
        self.socket.bind(self.server_bind_addr)

        # Build MecDriver, which owns movement-related data
        self.driver = md_mod.MecDriver()

        # Build WheelGunner, which owns firing-related data
        self.gunner = wg_mod.WheelGunner()

        # Build follower, which owns line following-related data
        self.follower = f_mod.Follower()

    def publish(self):
        """Publish information about bot."""
        self.logger.info("PubServer publishing on {}".format(
                                            self.server_bind_addr))

        while True:
            self.pub_drive_motor_br_detail()
            self.pub_drive_motor_fr_detail()
            self.pub_drive_motor_bl_detail()
            self.pub_drive_motor_fl_detail()
            self.pub_gun_motor_detail()
            self.pub_turret_detail()
            self.pub_gun_speed()
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

    def pub_drive_motor_br_detail(self):
        """Publish all info about back right drive motor."""
        br_motor = self.driver.motors["back_right"]
        self.socket.send("drive_motor_br_detail {}".format(br_motor))

    def pub_drive_motor_fr_detail(self):
        """Publish all info about front right drive motor."""
        fr_motor = self.driver.motors["front_right"]
        self.socket.send("drive_motor_fr_detail {}".format(fr_motor))

    def pub_drive_motor_bl_detail(self):
        """Publish all info about back left drive motor."""
        bl_motor = self.driver.motors["back_left"]
        self.socket.send("drive_motor_bl_detail {}".format(bl_motor))

    def pub_drive_motor_fl_detail(self):
        """Publish all info about front left drive motor."""
        fl_motor = self.driver.motors["front_left"]
        self.socket.send("drive_motor_fl_detail {}".format(fl_motor))

    def pub_gun_motor_detail(self):
        """Publish all info about gun motors"""
        for motor in self.gunner.motors:
            self.socket.send("gun_motor_detail {}".format(motor))

    def pub_turret_detail(self):
        """Publish all info about turret servos."""
        self.socket.send("turret_detail {}".format(self.gunner.turret))

    def pub_gun_speed(self):
        """Publish speed of gun motors."""
        self.socket.send("gun_speed {}".format(self.gunner.wheel_speed))

    def pub_turret_yaw(self):
        """Publish yaw angle of turret."""
        self.socket.send("turret_yaw {}".format(self.gunner.turret.yaw))

    def pub_turret_pitch(self):
        """Publish pitch angle of turret."""
        self.socket.send("turret_pitch {}".format(self.gunner.turret.pitch))

    def pub_drive_motor_br_speed(self):
        """Publish speed of back right drive motor."""
        speed = self.driver.motors["back_right"].speed
        self.socket.send("drive_motor_br_speed {}".format(speed))

    def pub_drive_motor_fr_speed(self):
        """Publish speed of front right drive motor."""
        speed = self.driver.motors["front_right"].speed
        self.socket.send("drive_motor_fr_speed {}".format(speed))

    def pub_drive_motor_bl_speed(self):
        """Publish speed of back left drive motor."""
        speed = self.driver.motors["back_left"].speed
        self.socket.send("drive_motor_bl_speed {}".format(speed))

    def pub_drive_motor_fl_speed(self):
        """Publish speed of front left drive motor."""
        speed = self.driver.motors["front_left"].speed
        self.socket.send("drive_motor_fl_speed {}".format(speed))

    def pub_drive_motor_br_dir(self):
        """Publish direction of back right drive motor."""
        direction = self.driver.motors["back_right"].direction
        self.socket.send("drive_motor_br_dir {}".format(direction))

    def pub_drive_motor_fr_dir(self):
        """Publish direction of front right drive motor."""
        direction = self.driver.motors["front_right"].direction
        self.socket.send("drive_motor_fr_dir {}".format(direction))

    def pub_drive_motor_bl_dir(self):
        """Publish direction of back left drive motor."""
        direction = self.driver.motors["back_left"].direction
        self.socket.send("drive_motor_bl_dir {}".format(direction))

    def pub_drive_motor_fl_dir(self):
        """Publish direction of front left drive motor."""
        direction = self.driver.motors["front_left"].direction
        self.socket.send("drive_motor_fl_dir {}".format(direction))

    def pub_drive_motor_br_vel(self):
        """Publish velocity of back right drive motor."""
        velocity = self.driver.motors["back_right"].velocity
        self.socket.send("drive_motor_br_vel {}".format(velocity))

    def pub_drive_motor_fr_vel(self):
        """Publish velocity of front right drive motor."""
        velocity = self.driver.motors["front_right"].velocity
        self.socket.send("drive_motor_fr_vel {}".format(velocity))

    def pub_drive_motor_bl_vel(self):
        """Publish velocity of back left drive motor."""
        velocity = self.driver.motors["back_left"].velocity
        self.socket.send("drive_motor_bl_vel {}".format(velocity))

    def pub_drive_motor_fl_vel(self):
        """Publish velocity of front left drive motor."""
        velocity = self.driver.motors["front_left"].velocity
        self.socket.send("drive_motor_fl_vel {}".format(velocity))

    def pub_irs(self):
        """Publish IR readings from all sensors."""
        reading = self.follower.irs.read_all_arrays()
        self.socket.send("ir_front {}".format(reading["front"]))
        self.socket.send("ir_back {}".format(reading["back"]))
        self.socket.send("ir_left {}".format(reading["left"]))
        self.socket.send("ir_right {}".format(reading["right"]))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        pub_server = PubServer(sys.argv[1])
    else:
        pub_server = PubServer()
    pub_server.publish()
