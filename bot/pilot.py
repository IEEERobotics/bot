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

    def find_start_condition(self):
        self.call('switch', 'detect_switch_orientation')

    def move(self, speed, angle):
        self.call('driver', 'move',
                  {'speed': speed, 'angle': angle})

    def drive(self, speed, angle, duration):
        return self.call('driver', 'drive',
                         {'speed': speed, 'angle': angle,
                          'duration': duration})

    def goto_block_zone_B(self):
        return self.call('nav', 'goto_block_zone_B')

    def goto_railcar(self):
        return self.call('nav', 'goto_railcar')

    def run(self):
        """Main pilot interface with outside world.
        start script will call, and pilot will handle all other logic.
        """

        #self.call('switch', 'test')
        val = self.find_start_condition()
        # Only on of these values will occur. Find which
        if val is 0 or 3:
            self.ctrl_client.exit_server()
            return
        # Left or Right?
        if val is 1:
        # Left or Right?
        if val is 2:

if __name__ == "__main__":
    Pilot().run()
