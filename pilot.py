"""Autonomous control client that solves IEEE Hardware Competition 2014."""

import sys
import lib.lib as lib
import client.ctrl_client as ctrl_client_mod
import client.sub_client as sub_client_mod


class Pilot:
    """Autonomous control client based on comprehensive state machine."""

    State = lib.Enum(('START', 'JERK', 'FIND_LINE', 'OSCILLATE',
                      'FOLLOW', 'CENTER_ON_X', 'CHOOSE_DIR_X',
                      'CENTER_ON_BLUE', 'AIM', 'FIRE',
                      'CHOOSE_DIR_BLUE', 'TURN_BACK',
                      'CENTER_ON_RED', 'FINISH'))

    def __init__(self, ctrl_addr="tcp://127.0.0.1:60000",
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
        self.heading = 0  # TODO: Ensure starting direction is correct
        self.blue_blocks = 0  # no. of blue blocks found and centered on
        self.darts_fired = 0  # no. of darts fired

    def run(self):
        # Start indefinite loop to run through states till FINISH
        last_state = None  # to detect state changes, mainly for debugging
        while self.state != self.State.FINISH:
            if self.state != last_state:
                self.logger.info(str(self))
                last_state = self.state

            # TODO: Require different systems to expose the desired API calls
            if self.state == self.State.START:
                # NOTE: follower must wrap color_sensor and expose is_* methods
                if self.call('follower', 'is_start') == True:  # start signal
                    self.state = self.State.JERK
            elif self.state == self.State.JERK:
                self.call('driver', 'jerk')  # takes time
                self.state = self.State.FIND_LINE
            elif self.state == self.State.FIND_LINE:
                if self.call('follower', 'is_on_line') == True:  # on line
                    self.state = self.State.FOLLOW
                else:
                    self.state = self.State.OSCILLATE
            elif self.state == self.State.OSCILLATE:
                self.call('follower', 'oscillate')  # takes time
                self.state = self.State.FIND_LINE
            elif self.state == self.State.FOLLOW:
                self.call('follower', 'follow', { 'heading': self.heading })
                # When follower is done following, one of the following is true
                if self.call('follower', 'is_on_x') == True:  # intersection
                    self.state = self.State.CENTER_ON_X
                elif self.call('follower', 'is_on_blue') == True:  # blue block
                    self.state = self.State.CENTER_ON_BLUE
                elif self.call('follower', 'is_on_red') == True:  # red block
                    self.state = self.State.CENTER_ON_RED
                elif self.call('follower', 'is_end_of_line') == True:  # EOL
                    self.state = self.State.TURN_BACK
                elif self.call('follower', 'is_on_line') == False:  # at sea
                    self.state = self.State.FIND_LINE
                else:
                    # Something wrong? Remain in FOLLOW state to try again
                    self.logger.error("Unknown follower.follow result!")
            elif self.state == self.State.CENTER_ON_X:
                self.call('follower', 'center_on_x')  # takes time
                self.state = self.State.CHOOSE_DIR_X  # assume centering worked
            elif self.state == self.State.CHOOSE_DIR_X:
                self.heading = (self.heading + 90) % 360  # always turn left
                self.state = self.State.FOLLOW
            elif self.state == self.State.CENTER_ON_BLUE:
                self.call('follower', 'center_on_blue')
                self.blue_blocks += 1
                # TODO: Wait for 3 secs., or ensure aiming takes that long?
                self.state = self.State.AIM
            elif self.state == self.State.AIM:
                # TODO: Ask localizer for block position, pass it to gunner
                # TODO: Turn on laser here? (for testing runs, at least?)
                self.call('gunner', 'aim_turret')
                # TODO: Spin up wheel gun here (per shot), or at start?
                self.state = self.State.FIRE
            elif self.state == self.State.FIRE:
                self.call('gun', 'fire')
                self.darts_fired += 1
                # TODO: Spin down wheel gun here (per shot); also laser
                self.state = self.State.CHOOSE_DIR_BLUE  # same as TURN_BACK?
            elif self.state == self.State.CHOOSE_DIR_BLUE:
                self.heading = (self.heading + 180) % 360  # turn around
                self.state = self.State.FOLLOW
            elif self.state == self.State.TURN_BACK:
                self.heading = (self.heading + 180) % 360  # turn around
                self.state = self.State.FOLLOW
            elif self.state == self.State.CENTER_ON_RED:
                self.call('follower', 'center_on_red')
                self.state = self.State.FINISH

        self.logger.info(str(self))  # terminal state report
        self.logger.info("Done!")

    def call(self, obj_name, method_name, param_dict=dict()):
        """Light wrapper around ctrl_client to handle result unpacking."""
        result = self.ctrl_client.call(obj_name, method_name, param_dict)
        if result['type'] == 'error':
            self.logger.error("API call error: {}".format(result['msg']))
            return None
        else:
            return result['call_return']

    def __str__(self):
        return "[{}] heading: {}, blue_blocks: {}, darts_fired: {}".format(
            self.State.toString(self.state), self.heading, self.blue_blocks,
            self.darts_fired)


if __name__ == "__main__":
    Pilot().run()
