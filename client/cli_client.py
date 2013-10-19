"""Client for sending commands to the bot's server via CLI."""

import os

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
        """Cleans up output when ctrl+d is used to exit client."""
        print
        return True

    def do_fire(self, raw_args):
        """fire <X angle> <Y angle> <speed>
        Set turret to angle (0-180), wheels to speed (0-100) and fire dart."""
        # Get and validate arguments
        args = raw_args.split()
        if len(args) != 3:
            print "Invalid command, see help [cmd]."
            return
        x, y, speed = args

        # Issue commands to server
        self.logger.info("Firing x: {}, y: {}, speed: {}".format(x, y, speed))
        self.send_aim(x, y)
        self.send_fire_speed(speed)
        self.send_fire()

    def do_aim(self, raw_args):
        """aim <X angle> <Y angle>
        Set turret to given X and Y angles (0-180)."""
        # Get and validate arguments
        args = raw_args.split()
        if len(args) != 2:
            print "Invalid command, see help [cmd]."
            return
        x, y = args

        # Issue commands to server
        self.logger.info("Aiming x: {}, y: {}".format(x, y))
        self.send_aim(x, y)

    def do_kill(self, raw_args):
        """Kill the server."""
        self.send_die()
