"""Autonomous control client that solves IEEE Hardware Competition 2014."""

import sys

import bot.lib.lib as lib
import bot.client.ctrl_client as ctrl_client_mod
import bot.client.sub_client as sub_client_mod


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

        # Initialize other members
        self.state = self.State.START
        self.heading = 180
        self.max_intersections = max_intersections  # total on course
        self.intersections = 0  # no. of intersections seen

    def __str__(self):
        return "[{}] heading: {}, intersections: {}, blue_blocks: {}, \
        darts_fired: {}".format(
            self.State.toString(self.state),
            self.intersections,
            self.heading,
            self.blue_blocks,
            self.darts_fired)

    def run(self):
        self.logger.info("Starting attack run")
        # Start indefinite loop to run through states till FINISH
        last_state = None  # to detect state changes, mainly for debugging

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

    def heading_to_driver_angle(self, heading):
        """Convert bot heading to raw angle for driver."""
        # NOTE(napratin,3/13): Currently follower uses 180 = front,
        #   while driver uses 0 = front, hence the need for conversion.
        return (heading + 180) % 360


if __name__ == "__main__":
    Pilot().run()
