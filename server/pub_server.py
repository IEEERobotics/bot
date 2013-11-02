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
        self.socket.bind(self.config["pub_server_addr"])

        # Build MecDriver, which owns movement-related data
        self.driver = md_mod.MecDriver()

        # Build WheelGunner, which owns firing-related data
        self.gunner = wg_mod.WheelGunner()

        # Build follower, which owns line following-related data
        self.follower = f_mod.Follower()

    def publish(self):
        """Publish information about bot."""
        self.logger.info("PubServer publishing on {}".format(
                                            self.config["pub_server_addr"]))

        while True:
            # Send motor info
            self.socket.send("motors {}".format(self.driver))
            sleep(.5)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        pub_server = PubServer(sys.argv[1])
    else:
        pub_server = PubServer()
    pub_server.publish()
