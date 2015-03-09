"""Autonomous control client that solves IEEE Hardware Competition 2014."""

import sys

import bot.lib.lib as lib
import bot.client.ctrl_client as ctrl_client_mod
import bot.client.sub_client as sub_client_mod

import bot.activity_solver as act_mod

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

    def build_act_solvers(self):
        """ Instantiates and returns dict of objects related to activity solver.
        """
        
        # TODO(AhmedSamara): Build activity solvers for the rest of the activities.
        acts = dict()
        # Todo(AhemdSamara): Populate with solvers as they're made.
        return acts
        

    def run(self):
        """Main pilot interface with outside world.
        start script will call, and pilot will handle all other logic.
        """
        
        # Begin run.
        
        # wait for Start signal to indicate time to run.

        self.acts = self.build_act_solvers()

        for activity in self.acts:
            # follow to intersection.

            # orient self toward activity.

            # solve activity.

if __name__ == "__main__":
    Pilot().run()
