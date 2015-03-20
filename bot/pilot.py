"""Autonomous control client that solves IEEE Hardware Competition 2014."""

import sys

import bot.lib.lib as lib
import bot.client.ctrl_client as ctrl_client_mod
import bot.client.sub_client as sub_client_mod

import bot.activity_solver.simon_solver as simon_mod
import bot.activity_solver.rubiks_solver as rubiks_mod
import bot.activity_solver.etch_sketch_solver as etch_mod


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
        self.ITEM_BACKUP_TIME = 5 
        # Order in which activities are solved.
        self.acts = ["simon", "etch", "rubiks", "card"]

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

    def drive(self, speed, direction):
        self.call('driver', 'move', 
                {'speed':speed, 'direction': direction})

    def wait_for_start(self):
        """Waits for color sensor to say it sees start signal.
        """

        return self.call('color_sensor', 'watch_for_not_color', 
                    {color:"red", timeout:180})

    def follow_call(self):
        """Helper function for calling line_follower.
        Will kick out at intersection.
        """
        return dir_of_intersection = \
                self.call('follower', 'analog_state')

    def rotate_90(self, direction):
        """call on driver api with whatever args are needed 
        Pass either "cc" or "c".
        """
        
        return self.call('driver', 'rough_rotate_90',
                         {'direction':direction}) 

    def solve_activity(self, activity):
        """pass name of activity to solve, will fix as needed.
        Choices are:
            etch, rubiks, simon, card
        """

        return self.call(activity, 'solve')

    def follow_ignoring_turns(self):
        while True:
            turn_dir = self.follow()
            
            # Continue going around runs until you hit intersect
            if turn_dir == "intersection":
                break
            else:
                self.rotate_90(turn_dir)
        return turn_dir
         
    def run(self):
        """Main pilot interface with outside world.
        start script will call, and pilot will handle all other logic.
        """
        
        # wait for Start signal to indicate time to run.
        self.wait_for_start()

        for activity in self.acts:
            print "solving: {}".format(activity)
            # Follow to intersection.
            self.follow_ignoring_turns() 
           
            # Orient self towards activity.
            # TODO(AhmedSamara): determine how to actually do that.
            # Possible Solutions: 
            #  - series of switches to hardcode location.
            #  - Follower telling location.

            self.solve_activity(activity)
            
            # Leave box and return to path.
            self.drive(50, 180)
            time.sleep(self.ITEM_BACKUP_TIME)
            self.drive(0, 0)

            self.rotate_90("right")
            self.rotate_90("right")
            
            # line follow back to path
            self.follow_ignoring_turns()

            # turn to path
            # Opposite of previous direction.

        # follow_to_block (finish line!)

if __name__ == "__main__":
    Pilot().run()
