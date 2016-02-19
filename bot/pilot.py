"""Autonomous control client that solves IEEE Hardware Competition 2016.
"""

import sys
import time

import lib.lib as lib
import client.ctrl_client as ctrl_client_mod
import client.sub_client as sub_client_mod


class Pilot:

    """Autonomous control client based on comprehensive state machine."""

    def __init__(self,
                 ctrl_addr="tcp://127.0.0.1:60000",
                 sub_addr="tcp://127.0.0.1:60001"):

        # Get config, build logger
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        # Build control client
        try:
            self.ctrl_client = ctrl_client_mod.CtrlClient(ctrl_addr)
        except Exception, e:
            self.logger.error("Couldn't build CtrlClient; ctrl_addr: {},"
                              " error: {}".format(ctrl_addr, e))
            sys.exit(-1)

        # Build sub client
        try:
            self.sub_client = sub_client_mod.SubClient(sub_addr)
        except Exception, e:
            self.logger.error("Couldn't build SubClient; sub_addr: {},"
                              " error: {}".format(sub_addr, e))
            sys.exit(-1)

    def call(self, obj_name, method_name, param_dict=dict()):
        """Light wrapper around ctrl_client to handle result unpacking."""
        result = self.ctrl_client.call(obj_name, method_name, param_dict)
        if result['type'] == 'error':
            self.logger.error("API call error: {}".format(result['msg']))
            return None
        else:
            return result['call_return']

    def bail(self, msg):
        """Log error message and exit cleanly, stopping all systems.

        :param msg: Error message to log.
        :type msg: string

        """
        self.logger.error("Can't handle follower result: {}".format(msg))
        self.call('ctrl', 'stop_full')
        sys.exit(1)

    def move(self, speed, angle):
        self.call('driver', 'move',
                  {'speed': speed, 'angle': angle})

    def drive(self, speed, angle, duration):
        return self.call('driver', 'drive',
                         {'speed': speed, 'angle': angle,
                          'duration': duration})

    def wait_for_start(self):
        """Waits for color sensor to say it sees start signal.
        """

        return self.call('color_sensor', 'watch_for_not_color',
                         {'color': 'red', "timeout": 180})

    def wait_for_ready(self):
        return self.call('color_sensor', 'wait_for_ready')

    def run(self):
        """Main pilot interface with outside world.
        start script will call, and pilot will handle all other logic.
        """

        # wait for Start signal to indicate time to run.
        # self.wait_for_start()
        time.sleep(10)
        self.wait_for_ready()
        self.drive(40, 0, 0.7)  # Leave starting block
        # Move towards the blocks; stop when north sensors detect wall.
        # Move towards the rail cars



if __name__ == "__main__":
    Pilot().run()
