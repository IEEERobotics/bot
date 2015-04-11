"""Autonomous control client that solves IEEE Hardware Competition 2014."""

import sys
import time

import lib.lib as lib
import client.ctrl_client as ctrl_client_mod
import client.sub_client as sub_client_mod

import activity_solver.simon_solver as simon_mod
import activity_solver.rubiks_solver as rubiks_mod
import activity_solver.etch_sketch_solver as etch_mod


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
        self.ITEM_BACKUP_TIME = 0.2 
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

    def move(self, speed, angle):
        self.call('driver', 'move', 
                {'speed':speed, 'angle': angle})

    def drive(self, speed, angle, duration):
        return self.call('driver', 'drive', 
            {'speed':speed, 'angle':angle, 'duration':duration})

    def wait_for_start(self):
        """Waits for color sensor to say it sees start signal.
        """

        return self.call('color_sensor', 'watch_for_not_color', 
                    {'color':'red', "timeout":180})

    def follow(self):
        """Helper function for calling line_follower.
        Will kick out at intersection.
        """
        dir_of_intersection = \
                self.call('follower', 'analog_state')

        return dir_of_intersection

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
        return self.call('follower','follow_ignoring_turns')
        
    def find_dir_of_turn(self):
        return self.call('follower','find_dir_of_turn')

    def find_dir_of_int(self):
        return self.call('follower','find_dir_of_int')
       
    def rotate_to_line(self, direction):
        return self.call('follower','rotate_to_line', {'direction':direction})

    def wait_for_ready(self):
        return self.call('color_sensor','wait_for_ready')

    def run(self):
        """Main pilot interface with outside world.
        start script will call, and pilot will handle all other logic.
        """
        
        # wait for Start signal to indicate time to run.
        # self.wait_for_start()
        time.sleep(4)
        self.drive(40,0,0.7) # Leave starting block

        for activity in self.acts:

            # Follow to intersection.
            self.follow_ignoring_turns()
            
            # keep track of direction of branch for returning to main path.
            act_dir = self.find_dir_of_int() 
            
            self.rotate_to_line(act_dir)

            # go to act.
            self.follow_ignoring_turns()

            # Activities we aren't solving.
            if activity == 'card':
                self.drive(40,0,0.2)
                time.sleep(1)
                self.drive(40,180,0.2)
            elif activity == 'simon':
                self.logger.debug("Not doing simon")
            else:
                self.solve_activity(activity)
            
            # Leave box and return to path.
            self.move(40, 180)
            time.sleep(self.ITEM_BACKUP_TIME)
            self.move(0, 0)

            self.rotate_90('right')
            time.sleep(0.5)
            self.rotate_to_line('right')
            
            # line follow back to path
            self.follow_ignoring_turns()

            # turn back to path
            if act_dir == 'left':
                self.rotate_to_line('right')
            elif act_dir == 'right':
                self.rotate_to_line('left')
            else:
                # error case but somehow possible.
                # Guess turn direction.
                self.rotate_to_line('right')


        self.follow_ignoring_turns()
        self.drive(40,0,0.5)

if __name__ == "__main__":
    Pilot().run()
