"""Client for sending commands to the bot's server via CLI."""

import os
import sys

import lib.lib as lib
import server.server as server
import client
import cmd


class CLIClient(client.Client, cmd.Cmd):

    """Send user commands to server running on the bot."""

    prompt = "bot$ "

    def __init__(self):
        """Run setup code."""
        client.Client.__init__(self)
        cmd.Cmd.__init__(self)

    def do_shell(self, cmd):
        """Allows normal shell commands to be run."""
        os.system(cmd)

    def do_EOF(self, line):
        """Cleans up when ctrl+d is used to exit client."""
        self.cleanUp()
        print
        return True

    def do_fire(self, raw_args):
        """fire <X angle> <Y angle> <speed>
        Set turret to angle (0-180), wheels to speed (0-100) and fire dart."""
        # Get and validate arguments
        try:
            x, y, speed = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        # Issue commands to server
        self.logger.info("Firing x: {}, y: {}, speed: {}".format(x, y, speed))
        self.send_aim(x, y)
        self.send_fire_speed(speed)
        self.send_fire()

    def do_gun_speed(self, raw_args):
        """gun_speed <speed>
        Spin gun wheels at given speed as percent of max (0-100)."""
        # Get and validate arguments
        try:
            speed = raw_args.split()[0]
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        # Issue commands to server
        self.logger.info("Gun speed: {}".format(speed))
        self.send_fire_speed(speed)

    def do_aim(self, raw_args):
        """aim <X angle> <Y angle>
        Set turret to given X and Y angles (0-180)."""
        # Get and validate arguments
        try:
            x, y = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        # Issue commands to server
        self.logger.info("Aiming x: {}, y: {}".format(x, y))
        self.send_aim(x, y)

    def do_push_dart(self, raw_args):
        """push_dart
        Advance dart into gun wheels."""
        # Issue commands to server
        self.logger.info("Advancing dart")
        self.send_fire()

    def do_fst(self, raw_args):
        """fst <forward speed> <strafe speed> <turn speed>
        Set bot to drive at the given speeds."""
        # Get and validate arguments
        try:
            fwd, strafe, turn = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        # Issue commands to server
        self.logger.info("Moving fwd: {}, strafe: {}, turn: {}".format(fwd,
                                                                       strafe,
                                                                       turn))
        self.send_fwd_strafe_turn(fwd, strafe, turn)

    def do_move(self, raw_args):
        """move <speed> <angle>
        Translate the bot. Speed is percent of max (0-100), angle
        is in degrees (0-360, 90=left, 270=right)."""
        # Get and validate arguments
        try:
            speed, angle = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        # Issue commands to server
        self.logger.info("Moving speed: {}, angle: {}".format(speed, angle))
        self.send_move(speed, angle)

    def do_rotate(self, raw_args):
        """rotate <speed>
        Rotate at given speed (-100 to 100, positive counterclockwise)."""
        # Get and validate arguments
        try:
            speed = raw_args.split()[0]
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        # Issue commands to server
        self.logger.info("Rotate speed: {}".format(speed))
        self.send_rotate(speed)

    def do_die(self, raw_args):
        """Close client and server."""
        self.cleanUp()
        sys.exit(0)

    def do_kill(self, raw_args):
        """Kill the server."""
        self.send_die()
